package ca.ulaval.glo4003.application.data.model;

import java.util.Arrays;

public enum DataSource {
  OPEN_FOOD_FACTS("open_food_facts", ""),
  CANADIAN_NUTRIENT_FILE("canadian_nutrient_file", "FOOD NAME.csv"),
  EXTENDED_RECIPES_DATASET("extended_recipes_dataset", "recipes_extended.json");

  private final String rawName;
  private final String mainFileSuffix;

  DataSource(String rawName, String mainFileSuffix) {
    this.rawName = rawName;
    this.mainFileSuffix = mainFileSuffix;
  }

  public String rawName() {
    return rawName;
  }

  public String mainFileSuffix() {
    return mainFileSuffix;
  }

  public static DataSource fromRawName(String rawName) {
    return Arrays.stream(values())
        .filter(source -> source.rawName.equals(rawName))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("Unknown raw source: " + rawName));
  }
}
