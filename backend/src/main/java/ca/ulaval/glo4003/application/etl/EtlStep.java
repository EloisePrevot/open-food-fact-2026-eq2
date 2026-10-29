package ca.ulaval.glo4003.application.etl;

import java.util.List;
import java.util.stream.Stream;

public enum EtlStep {
  EXTRACT("extraction des sources vers PostgreSQL", false, "--load-raw", "all"),
  TRANSFORM("nettoyage de PostgreSQL vers MongoDB", true, "--load-mongo", "--skip-up-to-date"),
  LOAD("indexation de PostgreSQL vers Qdrant", true, "--load-qdrant", "--skip-up-to-date");

  private static final String LIMIT_OPTION = "--limit";

  private final String description;
  private final boolean limitable;
  private final List<String> arguments;

  EtlStep(String description, boolean limitable, String... arguments) {
    this.description = description;
    this.limitable = limitable;
    this.arguments = List.of(arguments);
  }

  public String description() {
    return description;
  }

  public List<String> arguments(int limit) {
    if (!limitable) {
      return arguments;
    }
    return Stream.concat(arguments.stream(), Stream.of(LIMIT_OPTION, String.valueOf(limit)))
        .toList();
  }
}
