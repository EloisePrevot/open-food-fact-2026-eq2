package ca.ulaval.glo4003.persistence.postgres;

import ca.ulaval.glo4003.application.data.RawRecordRepository;
import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.data.model.RawReference;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Optional;

public class PostgresRawRecordRepository implements RawRecordRepository {

  private static final String FIND_ARTIFACT =
      """
      SELECT source, to_char(imported_at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
          AS imported_at
      FROM raw_artifacts WHERE artifact_id = ?
      """;

  private static final String FIND_RECORD_PAYLOAD =
      """
      SELECT payload_json::text AS payload FROM raw_records
      WHERE artifact_id = ? AND record_ordinal = ?
      """;

  private static final String FIND_OFF_PRODUCT_PAYLOAD =
      """
      SELECT (to_jsonb(product) - 'record_ordinal')::text AS payload FROM off_products product
      WHERE record_ordinal = ?
      """;

  private static final String OFF_PRODUCTS_TABLE = "off_products";
  private static final String RAW_RECORDS_TABLE = "raw_records";
  private static final String TABLE_EXISTS = "SELECT to_regclass(?) IS NOT NULL AS present";
  private static final String COUNT_OFF_PRODUCTS =
      "SELECT count(*) AS record_count FROM off_products";
  private static final String COUNT_LATEST_MAIN_FILE_RECORDS =
      """
      SELECT count(*) AS record_count FROM raw_records
      WHERE artifact_id = (
          SELECT artifact_id FROM raw_artifacts
          WHERE source = ? AND relative_path LIKE ?
          ORDER BY artifact_id DESC LIMIT 1)
      """;

  private final PersistenceClients persistenceClients;

  public PostgresRawRecordRepository(PersistenceClients persistenceClients) {
    this.persistenceClients = persistenceClients;
  }

  @Override
  public Optional<RawRecord> findByReference(RawReference reference) {
    try (Connection connection = persistenceClients.openPostgresConnection()) {
      return findArtifact(connection, reference.artifactId())
          .flatMap(artifact -> findRecord(connection, artifact, reference));
    } catch (SQLException exception) {
      throw new PersistenceException("Lecture du brut impossible", exception);
    }
  }

  /**
   * Counts the raw records actually stored, not the size of the source file: the published dump
   * only holds the evaluated sample. A layer that was never extracted counts as zero.
   */
  @Override
  public long countBySource(DataSource source) {
    try (Connection connection = persistenceClients.openPostgresConnection()) {
      if (source == DataSource.OPEN_FOOD_FACTS) {
        return tableExists(connection, OFF_PRODUCTS_TABLE)
            ? count(connection, COUNT_OFF_PRODUCTS)
            : 0;
      }
      if (!tableExists(connection, RAW_RECORDS_TABLE)) {
        return 0;
      }
      return count(
          connection,
          COUNT_LATEST_MAIN_FILE_RECORDS,
          source.rawName(),
          "%" + source.mainFileSuffix());
    } catch (SQLException exception) {
      throw new PersistenceException("Comptage du brut impossible", exception);
    }
  }

  private static boolean tableExists(Connection connection, String table) throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(TABLE_EXISTS)) {
      statement.setString(1, table);
      try (ResultSet result = statement.executeQuery()) {
        return result.next() && result.getBoolean("present");
      }
    }
  }

  private static long count(Connection connection, String query, String... parameters)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(query)) {
      for (int index = 0; index < parameters.length; index++) {
        statement.setString(index + 1, parameters[index]);
      }
      try (ResultSet result = statement.executeQuery()) {
        return result.next() ? result.getLong("record_count") : 0;
      }
    }
  }

  private Optional<Artifact> findArtifact(Connection connection, long artifactId)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(FIND_ARTIFACT)) {
      statement.setLong(1, artifactId);
      try (ResultSet result = statement.executeQuery()) {
        if (!result.next()) {
          return Optional.empty();
        }
        return Optional.of(
            new Artifact(
                DataSource.fromRawName(result.getString("source")),
                result.getString("imported_at")));
      }
    }
  }

  private Optional<RawRecord> findRecord(
      Connection connection, Artifact artifact, RawReference reference) {
    try {
      return findPayload(connection, artifact.source(), reference)
          .map(
              payload ->
                  new RawRecord(
                      reference.identifiant(), artifact.source(), artifact.importedAt(), payload));
    } catch (SQLException exception) {
      throw new PersistenceException("Lecture du brut impossible", exception);
    }
  }

  private Optional<String> findPayload(
      Connection connection, DataSource source, RawReference reference) throws SQLException {
    if (source == DataSource.OPEN_FOOD_FACTS) {
      return readPayload(connection, FIND_OFF_PRODUCT_PAYLOAD, reference.ordinal());
    }
    return readPayload(
        connection, FIND_RECORD_PAYLOAD, reference.artifactId(), reference.ordinal());
  }

  private Optional<String> readPayload(Connection connection, String query, long... parameters)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(query)) {
      for (int index = 0; index < parameters.length; index++) {
        statement.setLong(index + 1, parameters[index]);
      }
      try (ResultSet result = statement.executeQuery()) {
        return result.next() ? Optional.of(result.getString("payload")) : Optional.empty();
      }
    }
  }

  private record Artifact(DataSource source, String importedAt) {}
}
