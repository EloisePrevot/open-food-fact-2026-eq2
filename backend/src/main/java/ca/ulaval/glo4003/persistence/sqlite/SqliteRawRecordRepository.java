package ca.ulaval.glo4003.persistence.sqlite;

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

public class SqliteRawRecordRepository implements RawRecordRepository {

  private static final String FIND_BY_REFERENCE =
      """
      SELECT artifacts.source, artifacts.imported_at, records.payload_json
      FROM raw_records records
      JOIN raw_artifacts artifacts ON artifacts.artifact_id = records.artifact_id
      WHERE records.artifact_id = ? AND records.record_ordinal = ?
      """;

  private static final String COUNT_LATEST_MAIN_FILE =
      """
      SELECT record_count FROM raw_artifacts
      WHERE source = ? AND relative_path LIKE ?
      ORDER BY artifact_id DESC LIMIT 1
      """;

  private final PersistenceClients persistenceClients;

  public SqliteRawRecordRepository(PersistenceClients persistenceClients) {
    this.persistenceClients = persistenceClients;
  }

  @Override
  public Optional<RawRecord> findByReference(RawReference reference) {
    try (Connection connection = persistenceClients.openSqliteConnection();
        PreparedStatement statement = connection.prepareStatement(FIND_BY_REFERENCE)) {
      statement.setLong(1, reference.artifactId());
      statement.setLong(2, reference.ordinal());
      return readRawRecord(statement, reference.identifiant());
    } catch (SQLException exception) {
      throw new PersistenceException("Lecture du brut impossible", exception);
    }
  }

  @Override
  public long countBySource(DataSource source) {
    try (Connection connection = persistenceClients.openSqliteConnection();
        PreparedStatement statement = connection.prepareStatement(COUNT_LATEST_MAIN_FILE)) {
      statement.setString(1, source.rawName());
      statement.setString(2, "%" + source.mainFileSuffix());
      return readCount(statement);
    } catch (SQLException exception) {
      throw new PersistenceException("Comptage du brut impossible", exception);
    }
  }

  private Optional<RawRecord> readRawRecord(PreparedStatement statement, String identifiant)
      throws SQLException {
    try (ResultSet result = statement.executeQuery()) {
      if (!result.next()) {
        return Optional.empty();
      }
      return Optional.of(
          new RawRecord(
              identifiant,
              DataSource.fromRawName(result.getString("source")),
              result.getString("imported_at"),
              result.getString("payload_json")));
    }
  }

  private long readCount(PreparedStatement statement) throws SQLException {
    try (ResultSet result = statement.executeQuery()) {
      return result.next() ? result.getLong("record_count") : 0;
    }
  }
}
