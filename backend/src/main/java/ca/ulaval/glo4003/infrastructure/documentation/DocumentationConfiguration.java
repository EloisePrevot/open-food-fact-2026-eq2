package ca.ulaval.glo4003.infrastructure.documentation;

import java.nio.file.Path;

public record DocumentationConfiguration(Path readmePath) {

  private static final String README_PATH_ENVIRONMENT_VARIABLE = "README_PATH";
  private static final Path DEFAULT_README_PATH = Path.of("..", "README.md");

  public static DocumentationConfiguration fromEnvironment() {
    String readmePath = System.getenv(README_PATH_ENVIRONMENT_VARIABLE);
    return new DocumentationConfiguration(
        readmePath == null ? DEFAULT_README_PATH : Path.of(readmePath));
  }
}
