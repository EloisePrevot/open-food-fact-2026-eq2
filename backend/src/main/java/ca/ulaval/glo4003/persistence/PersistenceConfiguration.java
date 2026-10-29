package ca.ulaval.glo4003.persistence;

public record PersistenceConfiguration(
    String mongodbUri,
    String mongodbDatabase,
    String qdrantHost,
    int qdrantPort,
    String postgresJdbcUrl,
    String postgresUser,
    String postgresPassword) {

  private static final String MONGODB_URI_ENVIRONMENT_VARIABLE = "MONGODB_URI";
  private static final String MONGODB_DATABASE_ENVIRONMENT_VARIABLE = "MONGODB_DATABASE";
  private static final String QDRANT_HOST_ENVIRONMENT_VARIABLE = "QDRANT_HOST";
  private static final String QDRANT_PORT_ENVIRONMENT_VARIABLE = "QDRANT_PORT";
  private static final String POSTGRES_JDBC_URL_ENVIRONMENT_VARIABLE = "POSTGRES_JDBC_URL";
  private static final String POSTGRES_USER_ENVIRONMENT_VARIABLE = "POSTGRES_USER";
  private static final String POSTGRES_PASSWORD_ENVIRONMENT_VARIABLE = "POSTGRES_PASSWORD";

  private static final String DEFAULT_MONGODB_URI =
      "mongodb://root:root@localhost:27017/?authSource=admin";
  private static final String DEFAULT_MONGODB_DATABASE = "open_food_facts";
  private static final String DEFAULT_QDRANT_HOST = "localhost";
  private static final int DEFAULT_QDRANT_PORT = 6334;
  private static final String DEFAULT_POSTGRES_JDBC_URL =
      "jdbc:postgresql://localhost:5432/open_food_facts";
  private static final String DEFAULT_POSTGRES_USER = "postgres";
  private static final String DEFAULT_POSTGRES_PASSWORD = "postgres";

  public static PersistenceConfiguration fromEnvironment() {
    return new PersistenceConfiguration(
        getEnvironmentValue(MONGODB_URI_ENVIRONMENT_VARIABLE, DEFAULT_MONGODB_URI),
        getEnvironmentValue(MONGODB_DATABASE_ENVIRONMENT_VARIABLE, DEFAULT_MONGODB_DATABASE),
        getEnvironmentValue(QDRANT_HOST_ENVIRONMENT_VARIABLE, DEFAULT_QDRANT_HOST),
        Integer.parseInt(
            getEnvironmentValue(
                QDRANT_PORT_ENVIRONMENT_VARIABLE, String.valueOf(DEFAULT_QDRANT_PORT))),
        getEnvironmentValue(POSTGRES_JDBC_URL_ENVIRONMENT_VARIABLE, DEFAULT_POSTGRES_JDBC_URL),
        getEnvironmentValue(POSTGRES_USER_ENVIRONMENT_VARIABLE, DEFAULT_POSTGRES_USER),
        getEnvironmentValue(POSTGRES_PASSWORD_ENVIRONMENT_VARIABLE, DEFAULT_POSTGRES_PASSWORD));
  }

  private static String getEnvironmentValue(String name, String defaultValue) {
    return System.getenv().getOrDefault(name, defaultValue);
  }
}
