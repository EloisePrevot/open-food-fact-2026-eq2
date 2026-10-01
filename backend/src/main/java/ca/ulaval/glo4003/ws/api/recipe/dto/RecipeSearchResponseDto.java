package ca.ulaval.glo4003.ws.api.recipe.dto;

import java.util.List;

public class RecipeSearchResponseDto {
  public List<RecipeSummaryDto> recettes;

  public static class RecipeSummaryDto {
    public String identifiant;
    public String nom;
    public List<String> type;
    public int nbIngredients;
    public Double score;
  }
}
