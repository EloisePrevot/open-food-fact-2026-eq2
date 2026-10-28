package ca.ulaval.glo4003.infrastructure.embedding;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.within;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class OnnxTextEmbedderIT {

  private static final String QUERY = "un souper réconfortant d'hiver";
  private static final float[] FASTEMBED_FIRST_VALUES = {
    0.08910301f, -0.11646617f, 0.00328619f, 0.60722214f, 0.03934132f
  };

  @Test
  void givenFastembedModel_whenEmbedding_thenVectorMatchesPythonPipeline() {
    Path modelDirectory = EmbeddingConfiguration.fromEnvironment().modelDirectory();
    assumeTrue(Files.isDirectory(modelDirectory), "Modèle fastembed absent");

    float[] vector = new OnnxTextEmbedder(modelDirectory).embed(QUERY);

    assertThat(vector).hasSize(384);
    for (int index = 0; index < FASTEMBED_FIRST_VALUES.length; index++) {
      assertThat(vector[index]).isCloseTo(FASTEMBED_FIRST_VALUES[index], within(1e-4f));
    }
  }
}
