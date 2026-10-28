package ca.ulaval.glo4003.persistence.sqlite;

import static org.assertj.core.api.Assertions.assertThat;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.data.model.RawReference;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceConfiguration;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Optional;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class SqliteRawRecordRepositoryTest {

  private static final String PAYLOAD = "{\"FoodID\":\"2\",\"ScientificName\":\"\"}";
  private static final String SCHEMA =
      """
      CREATE TABLE raw_artifacts (
          artifact_id INTEGER PRIMARY KEY, source TEXT, relative_path TEXT,
          imported_at TEXT, record_count INTEGER);
      CREATE TABLE raw_records (
          artifact_id INTEGER, record_ordinal INTEGER, payload_json TEXT);
      INSERT INTO raw_artifacts VALUES
          (1, 'canadian_nutrient_file', 'cnf\\FOOD GROUP.csv', '2026-10-01', 23),
          (2, 'canadian_nutrient_file', 'cnf\\FOOD NAME.csv', '2026-10-01', 5690),
          (3, 'canadian_nutrient_file', 'cnf\\FOOD NAME.csv', '2026-10-02', 5700);
      """;

  @TempDir Path directory;

  private PersistenceClients persistenceClients;
  private SqliteRawRecordRepository repository;

  @BeforeEach
  void setUp() throws SQLException {
    persistenceClients =
        PersistenceClients.connect(
            new PersistenceConfiguration(
                "mongodb://localhost:27017",
                "test",
                "localhost",
                6334,
                "jdbc:sqlite:" + directory.resolve("raw.db")));
    try (Connection connection = persistenceClients.openSqliteConnection();
        Statement statement = connection.createStatement()) {
      statement.executeUpdate(SCHEMA.split(";")[0]);
      statement.executeUpdate(SCHEMA.split(";")[1]);
      statement.executeUpdate(SCHEMA.split(";")[2]);
      statement.executeUpdate(
          "INSERT INTO raw_records VALUES (3, 7, '" + PAYLOAD.replace("'", "''") + "')");
    }
    repository = new SqliteRawRecordRepository(persistenceClients);
  }

  @AfterEach
  void tearDown() {
    persistenceClients.close();
  }

  @Test
  void whenCountingSource_thenLatestMainFileCountIsReturned() {
    assertThat(repository.countBySource(DataSource.CANADIAN_NUTRIENT_FILE)).isEqualTo(5700);
  }

  @Test
  void givenSourceNeverExtracted_whenCounting_thenZeroIsReturned() {
    assertThat(repository.countBySource(DataSource.OPEN_FOOD_FACTS)).isZero();
  }

  @Test
  void givenReference_whenFinding_thenPayloadIsReturnedUnchanged() {
    Optional<RawRecord> rawRecord = repository.findByReference(new RawReference("cnf:2", 3, 7));

    assertThat(rawRecord)
        .contains(new RawRecord("cnf:2", DataSource.CANADIAN_NUTRIENT_FILE, "2026-10-02", PAYLOAD));
  }

  @Test
  void givenUnknownReference_whenFinding_thenEmptyIsReturned() {
    assertThat(repository.findByReference(new RawReference("cnf:2", 3, 8))).isEmpty();
  }
}
