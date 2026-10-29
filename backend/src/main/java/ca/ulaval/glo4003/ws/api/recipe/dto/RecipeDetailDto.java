package ca.ulaval.glo4003.ws.api.recipe.dto;

import java.util.List;

public class RecipeDetailDto {
  public String identifiant;
  public String nom;
  public String description;
  public List<String> type;
  public List<RecipeIngredientDto> ingredients;
  public List<String> etapes;

  public static class RecipeIngredientDto {
    public String nom;
    public String cle;
    public String texteOriginal;
  }
}
