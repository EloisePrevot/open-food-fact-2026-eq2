package ca.ulaval.glo4003.infrastructure.etl;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import ca.ulaval.glo4003.application.etl.EtlException;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

class PythonEtlRunnerTest {

  private static final Path CURRENT_DIRECTORY = Path.of(".");
  private static final String JAVA_COMMAND = ProcessHandle.current().info().command().orElseThrow();

  @Test
  void givenMissingExecutable_whenRunning_thenEtlExceptionIsThrown() {
    PythonEtlRunner runner = new PythonEtlRunner("commande-introuvable", CURRENT_DIRECTORY);

    assertThatThrownBy(() -> runner.run(List.of("--load-raw", "all")))
        .isInstanceOf(EtlException.class);
  }

  @Test
  void givenProcessExitingWithError_whenRunning_thenEtlExceptionIsThrown() {
    PythonEtlRunner runner = new PythonEtlRunner(JAVA_COMMAND, CURRENT_DIRECTORY);

    assertThatThrownBy(() -> runner.run(List.of("--load-raw", "all")))
        .isInstanceOf(EtlException.class)
        .hasMessageContaining("code");
  }
}
