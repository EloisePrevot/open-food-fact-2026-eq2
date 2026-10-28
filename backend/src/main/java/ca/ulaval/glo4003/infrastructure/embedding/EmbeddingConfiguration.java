package ca.ulaval.glo4003.infrastructure.embedding;

import java.nio.file.Path;

public record EmbeddingConfiguration(Path modelDirectory) {

  private static final String MODEL_DIRECTORY_ENVIRONMENT_VARIABLE = "EMBEDDING_MODEL_DIRECTORY";
  private static final String FASTEMBED_CACHE_DIRECTORY = "fastembed_cache";

  public static EmbeddingConfiguration fromEnvironment() {
    String directory = System.getenv(MODEL_DIRECTORY_ENVIRONMENT_VARIABLE);
    return new EmbeddingConfiguration(
        directory == null ? defaultFastembedCache() : Path.of(directory));
  }

  private static Path defaultFastembedCache() {
    return Path.of(System.getProperty("java.io.tmpdir"), FASTEMBED_CACHE_DIRECTORY);
  }
}
