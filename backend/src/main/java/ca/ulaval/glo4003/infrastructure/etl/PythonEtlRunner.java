package ca.ulaval.glo4003.infrastructure.etl;

import ca.ulaval.glo4003.application.etl.EtlException;
import ca.ulaval.glo4003.application.etl.EtlRunner;
import ca.ulaval.glo4003.application.etl.EtlService;
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PythonEtlRunner implements EtlRunner {

  private static final Logger LOGGER = LoggerFactory.getLogger(PythonEtlRunner.class);
  private static final List<String> LOAD_MODULE = List.of("-m", "load");

  private final String pythonCommand;
  private final Path eltDirectory;

  public PythonEtlRunner(String pythonCommand, Path eltDirectory) {
    this.pythonCommand = pythonCommand;
    this.eltDirectory = eltDirectory;
  }

  @Override
  public void run(List<String> arguments) {
    List<String> command = command(arguments);
    Process process = start(command);
    logOutput(process);
    int exitCode = waitFor(process);
    if (exitCode != 0) {
      throw new EtlException(String.join(" ", command) + " a terminé avec le code " + exitCode);
    }
  }

  private List<String> command(List<String> arguments) {
    return Stream.of(List.of(pythonCommand), LOAD_MODULE, arguments).flatMap(List::stream).toList();
  }

  private Process start(List<String> command) {
    ProcessBuilder builder =
        new ProcessBuilder(command).directory(eltDirectory.toFile()).redirectErrorStream(true);
    builder.environment().put("PYTHONIOENCODING", "utf-8");
    builder.environment().put("PYTHONUNBUFFERED", "1");
    try {
      return builder.start();
    } catch (IOException exception) {
      throw new EtlException("Impossible de lancer " + String.join(" ", command), exception);
    }
  }

  private void logOutput(Process process) {
    try (BufferedReader reader = process.inputReader(StandardCharsets.UTF_8)) {
      reader.lines().forEach(line -> LOGGER.info("{} {}", EtlService.LOG_PREFIX, line));
    } catch (IOException exception) {
      throw new EtlException("Lecture de la sortie du pipeline impossible", exception);
    }
  }

  private int waitFor(Process process) {
    try {
      return process.waitFor();
    } catch (InterruptedException exception) {
      Thread.currentThread().interrupt();
      process.destroy();
      throw new EtlException("Pipeline interrompu", exception);
    }
  }
}
