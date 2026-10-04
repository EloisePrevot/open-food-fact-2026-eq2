package ca.ulaval.glo4003.persistence;

import static org.assertj.core.api.Assertions.assertThat;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.concurrent.TimeUnit;
import org.bson.Document;
import org.junit.jupiter.api.Test;

class PersistenceClientsIT {
  private static final String MONGODB_URI = "mongodb://root:root@localhost:27017/?authSource=admin";
  private static final String MONGODB_DATABASE = "open_food_facts";
  private static final String QDRANT_HOST = "localhost";
  private static final int QDRANT_GRPC_PORT = 6334;
  private static final String SQLITE_JDBC_URL = "jdbc:sqlite::memory:";
  private static final String SQLITE_CONNECTION_QUERY = "SELECT 1";
  private static final String MONGODB_PING_COMMAND = "ping";
  private static final String MONGODB_SUCCESS_RESPONSE_KEY = "ok";
  private static final int PING_VALUE = 1;
  private static final long CONNECTION_TIMEOUT_SECONDS = 30;
  private static final int EXPECTED_SQLITE_VALUE = 1;

  @Test
  void connectsToMongoDbQdrantAndSqlite() throws Exception {
    PersistenceConfiguration configuration =
        new PersistenceConfiguration(
            MONGODB_URI, MONGODB_DATABASE, QDRANT_HOST, QDRANT_GRPC_PORT, SQLITE_JDBC_URL);

    try (PersistenceClients persistenceClients = PersistenceClients.connect(configuration)) {
      Document mongoResponse =
          persistenceClients
              .mongoDatabase()
              .runCommand(new Document(MONGODB_PING_COMMAND, PING_VALUE));

      persistenceClients
          .qdrantClient()
          .listCollectionsAsync()
          .get(CONNECTION_TIMEOUT_SECONDS, TimeUnit.SECONDS);

      try (Connection connection = persistenceClients.openSqliteConnection();
          Statement statement = connection.createStatement();
          ResultSet resultSet = statement.executeQuery(SQLITE_CONNECTION_QUERY)) {
        resultSet.next();

        assertThat(mongoResponse.getDouble(MONGODB_SUCCESS_RESPONSE_KEY)).isEqualTo(1.0);
        assertThat(resultSet.getInt(1)).isEqualTo(EXPECTED_SQLITE_VALUE);
      }
    }
  }
}
