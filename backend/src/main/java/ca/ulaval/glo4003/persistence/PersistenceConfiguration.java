package ca.ulaval.glo4003.persistence;

public record PersistenceConfiguration(
    String mongodbUri,
    String mongodbDatabase,
    String qdrantHost,
    int qdrantPort,
    String sqliteJdbcUrl) {

  private static final String MONGODB_URI_ENVIRONMENT_VARIABLE = "MONGODB_URI";
  private static final String MONGODB_DATABASE_ENVIRONMENT_VARIABLE = "MONGODB_DATABASE";
  private static final String QDRANT_HOST_ENVIRONMENT_VARIABLE = "QDRANT_HOST";
  private static final String QDRANT_PORT_ENVIRONMENT_VARIABLE = "QDRANT_PORT";
  private static final String SQLITE_JDBC_URL_ENVIRONMENT_VARIABLE = "SQLITE_JDBC_URL";

  private static final String DEFAULT_MONGODB_URI =
      "mongodb://root:root@localhost:27017/?authSource=admin";
  private static final String DEFAULT_MONGODB_DATABASE = "open_food_facts";
  private static final String DEFAULT_QDRANT_HOST = "localhost";
  private static final int DEFAULT_QDRANT_PORT = 6334;
  private static final String DEFAULT_SQLITE_JDBC_URL = "jdbc:sqlite:../etl/data/raw-data.db";

  public static PersistenceConfiguration fromEnvironment() {
    return new PersistenceConfiguration(
        getEnvironmentValue(MONGODB_URI_ENVIRONMENT_VARIABLE, DEFAULT_MONGODB_URI),
        getEnvironmentValue(MONGODB_DATABASE_ENVIRONMENT_VARIABLE, DEFAULT_MONGODB_DATABASE),
        getEnvironmentValue(QDRANT_HOST_ENVIRONMENT_VARIABLE, DEFAULT_QDRANT_HOST),
        Integer.parseInt(
            getEnvironmentValue(
                QDRANT_PORT_ENVIRONMENT_VARIABLE, String.valueOf(DEFAULT_QDRANT_PORT))),
        getEnvironmentValue(SQLITE_JDBC_URL_ENVIRONMENT_VARIABLE, DEFAULT_SQLITE_JDBC_URL));
  }

  private static String getEnvironmentValue(String name, String defaultValue) {
    return System.getenv().getOrDefault(name, defaultValue);
  }
}
