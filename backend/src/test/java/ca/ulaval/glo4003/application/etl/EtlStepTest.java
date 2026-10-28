package ca.ulaval.glo4003.application.etl;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;

class EtlStepTest {

  private static final int LIMIT = 500;

  @Test
  void givenExtract_whenGettingArguments_thenLimitIsIgnored() {
    assertThat(EtlStep.EXTRACT.arguments(LIMIT)).containsExactly("--load-raw", "all");
  }

  @Test
  void givenTransform_whenGettingArguments_thenLimitIsAppended() {
    assertThat(EtlStep.TRANSFORM.arguments(LIMIT))
        .containsExactly("--load-mongo", "--skip-up-to-date", "--limit", "500");
  }

  @Test
  void givenLoad_whenGettingArguments_thenLimitIsAppended() {
    assertThat(EtlStep.LOAD.arguments(LIMIT))
        .containsExactly("--load-qdrant", "--skip-up-to-date", "--limit", "500");
  }
}
