package ca.ulaval.glo4003.application.recipes.model;

import java.util.List;

public record RecipeDetailDocument(
    String identifiant,
    String nom,
    String description,
    List<String> types,
    List<RecipeIngredient> ingredients,
    List<String> etapes) {

  public record RecipeIngredient(String nom, String cle, String texteOriginal) {}
}
