package ca.ulaval.glo4003.infrastructure.etl;

import java.nio.file.Path;

public record EtlConfiguration(
    boolean runAtStartup, int limit, String pythonCommand, Path eltDirectory) {

  private static final String RUN_AT_STARTUP_ENVIRONMENT_VARIABLE = "ELT_AU_DEMARRAGE";
  private static final String LIMIT_ENVIRONMENT_VARIABLE = "ELT_LIMITE";
  private static final String PYTHON_ENVIRONMENT_VARIABLE = "ELT_PYTHON";
  private static final String DIRECTORY_ENVIRONMENT_VARIABLE = "ELT_DIRECTORY";

  private static final String DEFAULT_RUN_AT_STARTUP = "false";
  private static final String DEFAULT_LIMIT = "0";
  private static final String DEFAULT_PYTHON = "python";
  private static final String DEFAULT_DIRECTORY = "../elt";

  public EtlConfiguration {
    if (limit < 0) {
      throw new IllegalArgumentException(LIMIT_ENVIRONMENT_VARIABLE + " doit être positif ou 0.");
    }
  }

  public static EtlConfiguration fromEnvironment() {
    return new EtlConfiguration(
        Boolean.parseBoolean(
            getEnvironmentValue(RUN_AT_STARTUP_ENVIRONMENT_VARIABLE, DEFAULT_RUN_AT_STARTUP)),
        Integer.parseInt(getEnvironmentValue(LIMIT_ENVIRONMENT_VARIABLE, DEFAULT_LIMIT)),
        getEnvironmentValue(PYTHON_ENVIRONMENT_VARIABLE, DEFAULT_PYTHON),
        Path.of(getEnvironmentValue(DIRECTORY_ENVIRONMENT_VARIABLE, DEFAULT_DIRECTORY)));
  }

  private static String getEnvironmentValue(String name, String defaultValue) {
    return System.getenv().getOrDefault(name, defaultValue);
  }
}
