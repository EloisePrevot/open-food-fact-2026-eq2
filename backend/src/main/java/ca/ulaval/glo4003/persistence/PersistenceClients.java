package ca.ulaval.glo4003.persistence;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.QdrantGrpcClient;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public final class PersistenceClients implements AutoCloseable {
  private final MongoClient mongoClient;
  private final MongoDatabase mongoDatabase;
  private final QdrantClient qdrantClient;
  private final String postgresJdbcUrl;
  private final String postgresUser;
  private final String postgresPassword;

  private PersistenceClients(
      MongoClient mongoClient,
      MongoDatabase mongoDatabase,
      QdrantClient qdrantClient,
      String postgresJdbcUrl,
      String postgresUser,
      String postgresPassword) {
    this.mongoClient = mongoClient;
    this.mongoDatabase = mongoDatabase;
    this.qdrantClient = qdrantClient;
    this.postgresJdbcUrl = postgresJdbcUrl;
    this.postgresUser = postgresUser;
    this.postgresPassword = postgresPassword;
  }

  public static PersistenceClients connect(PersistenceConfiguration configuration) {
    MongoClient mongoClient = MongoClients.create(configuration.mongodbUri());
    return new PersistenceClients(
        mongoClient,
        mongoClient.getDatabase(configuration.mongodbDatabase()),
        new QdrantClient(
            QdrantGrpcClient.newBuilder(
                    configuration.qdrantHost(), configuration.qdrantPort(), false)
                .build()),
        configuration.postgresJdbcUrl(),
        configuration.postgresUser(),
        configuration.postgresPassword());
  }

  public MongoDatabase mongoDatabase() {
    return mongoDatabase;
  }

  public QdrantClient qdrantClient() {
    return qdrantClient;
  }

  public Connection openPostgresConnection() throws SQLException {
    return DriverManager.getConnection(postgresJdbcUrl, postgresUser, postgresPassword);
  }

  @Override
  public void close() {
    mongoClient.close();
    qdrantClient.close();
  }
}
