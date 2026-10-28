package ca.ulaval.glo4003.application.recipes.model;

import java.util.List;

public record RecipeDocument(
    String identifiant, String nom, List<String> types, int nbIngredients) {}
