package ca.ulaval.glo4003.infrastructure.embedding;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;

record ModelFiles(Path model, Path tokenizer) {

  private static final String MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2";
  private static final String MODEL_FILE = "model_optimized.onnx";
  private static final String TOKENIZER_FILE = "tokenizer.json";

  static ModelFiles locate(Path directory) {
    try (Stream<Path> paths = Files.walk(directory)) {
      Path model =
          paths
              .filter(ModelFiles::isModelFile)
              .findFirst()
              .orElseThrow(() -> missingModel(directory));
      return new ModelFiles(model, model.resolveSibling(TOKENIZER_FILE));
    } catch (IOException exception) {
      throw new EmbeddingException("Lecture du dossier " + directory + " impossible", exception);
    }
  }

  private static boolean isModelFile(Path path) {
    return path.getFileName().toString().equals(MODEL_FILE) && path.toString().contains(MODEL_NAME);
  }

  private static EmbeddingException missingModel(Path directory) {
    return new EmbeddingException(
        "Modèle " + MODEL_NAME + " introuvable dans " + directory + " (EMBEDDING_MODEL_DIRECTORY)");
  }
}
