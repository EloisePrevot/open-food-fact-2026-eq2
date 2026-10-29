package ca.ulaval.glo4003.persistence.postgres;

import static org.assertj.core.api.Assertions.assertThat;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.data.model.RawReference;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceConfiguration;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class PostgresRawRecordRepositoryDatabaseIT {

  private static final String JDBC_URL = "jdbc:postgresql://localhost:5432/open_food_facts";
  private static final String USER = "postgres";
  private static final String PASSWORD = "postgres";
  private static final String CNF_PAYLOAD = "{\"FoodID\": \"2\", \"ScientificName\": \"\"}";
  private static final String[] SCHEMA = {
    """
    CREATE TABLE raw_artifacts (
        artifact_id BIGINT PRIMARY KEY, source TEXT, relative_path TEXT,
        imported_at TIMESTAMPTZ, record_count BIGINT)
    """,
    "CREATE TABLE raw_records (artifact_id BIGINT, record_ordinal BIGINT, payload_json JSONB)",
    "CREATE TABLE off_products (record_ordinal BIGINT, code TEXT, product_name TEXT)",
    """
    INSERT INTO raw_artifacts VALUES
        (1, 'canadian_nutrient_file', 'cnf/FOOD GROUP.csv', '2026-10-01T00:00:00Z', 23),
        (2, 'canadian_nutrient_file', 'cnf/FOOD NAME.csv', '2026-10-01T00:00:00Z', 5690),
        (3, 'canadian_nutrient_file', 'cnf/FOOD NAME.csv', '2026-10-02T00:00:00Z', 5700),
        (4, 'open_food_facts', 'off.csv', '2026-10-02T00:00:00Z', 2)
    """,
    "INSERT INTO raw_records VALUES (3, 7, '" + CNF_PAYLOAD + "')",
    "INSERT INTO off_products VALUES (1, '054', 'Limonade'), (2, '055', NULL)"
  };

  private final String schema = "test_" + UUID.randomUUID().toString().replace("-", "");
  private PersistenceClients persistenceClients;
  private PostgresRawRecordRepository repository;

  @BeforeEach
  void setUp() throws SQLException {
    execute(JDBC_URL, "CREATE SCHEMA " + schema);
    String schemaUrl = JDBC_URL + "?currentSchema=" + schema;
    execute(schemaUrl, SCHEMA);
    persistenceClients =
        PersistenceClients.connect(
            new PersistenceConfiguration(
                "mongodb://localhost:27017", "test", "localhost", 6334, schemaUrl, USER, PASSWORD));
    repository = new PostgresRawRecordRepository(persistenceClients);
  }

  @AfterEach
  void tearDown() throws SQLException {
    persistenceClients.close();
    execute(JDBC_URL, "DROP SCHEMA " + schema + " CASCADE");
  }

  @Test
  void whenCountingSource_thenLatestMainFileCountIsReturned() {
    assertThat(repository.countBySource(DataSource.CANADIAN_NUTRIENT_FILE)).isEqualTo(5700);
  }

  @Test
  void givenSourceNeverExtracted_whenCounting_thenZeroIsReturned() {
    assertThat(repository.countBySource(DataSource.EXTENDED_RECIPES_DATASET)).isZero();
  }

  @Test
  void givenReference_whenFinding_thenPayloadIsReturned() {
    Optional<RawRecord> rawRecord = repository.findByReference(new RawReference("cnf:2", 3, 7));

    assertThat(rawRecord)
        .contains(
            new RawRecord(
                "cnf:2", DataSource.CANADIAN_NUTRIENT_FILE, "2026-10-02T00:00:00Z", CNF_PAYLOAD));
  }

  @Test
  void givenOffReference_whenFinding_thenProductRowIsReturnedAsJson() {
    Optional<RawRecord> rawRecord = repository.findByReference(new RawReference("off:054", 4, 1));

    assertThat(rawRecord.map(RawRecord::payloadJson))
        .contains("{\"code\": \"054\", \"product_name\": \"Limonade\"}");
  }

  @Test
  void givenUnknownReference_whenFinding_thenEmptyIsReturned() {
    assertThat(repository.findByReference(new RawReference("cnf:2", 3, 8))).isEmpty();
    assertThat(repository.findByReference(new RawReference("cnf:2", 99, 7))).isEmpty();
  }

  private static void execute(String url, String... statements) throws SQLException {
    try (Connection connection = DriverManager.getConnection(url, USER, PASSWORD);
        Statement statement = connection.createStatement()) {
      for (String sql : statements) {
        statement.executeUpdate(sql);
      }
    }
  }
}
