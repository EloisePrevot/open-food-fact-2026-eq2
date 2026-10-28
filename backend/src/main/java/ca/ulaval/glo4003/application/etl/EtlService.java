package ca.ulaval.glo4003.application.etl;

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.Executor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EtlService {

  public static final String LOG_PREFIX = "[ETL en arrière-plan]";

  private static final Logger LOGGER = LoggerFactory.getLogger(EtlService.class);

  private final EtlRunner runner;
  private final Executor executor;
  private final int limit;

  public EtlService(EtlRunner runner, Executor executor, int limit) {
    this.runner = runner;
    this.executor = executor;
    this.limit = limit;
  }

  public void startInBackground() {
    LOGGER.info(
        "{} Démarrage ({}). L'API reste disponible pendant le chargement.",
        LOG_PREFIX,
        describeLimit());
    executor.execute(this::runPipeline);
  }

  private void runPipeline() {
    Instant start = Instant.now();
    try {
      for (EtlStep step : EtlStep.values()) {
        runStep(step);
      }
      LOGGER.info("{} Terminé en {} s.", LOG_PREFIX, secondsSince(start));
    } catch (EtlException exception) {
      LOGGER.error(
          "{} Échec après {} s : {}", LOG_PREFIX, secondsSince(start), exception.getMessage());
    }
  }

  private void runStep(EtlStep step) {
    LOGGER.info(
        "{} Étape {}/{} : {}",
        LOG_PREFIX,
        step.ordinal() + 1,
        EtlStep.values().length,
        step.description());
    runner.run(step.arguments(limit));
  }

  private String describeLimit() {
    return limit == 0 ? "aucune limite" : "limite de " + limit + " documents par source";
  }

  private static long secondsSince(Instant start) {
    return Duration.between(start, Instant.now()).toSeconds();
  }
}
