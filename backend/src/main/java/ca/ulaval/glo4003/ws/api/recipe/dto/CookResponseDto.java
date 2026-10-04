package ca.ulaval.glo4003.ws.api.recipe.dto;

import java.util.List;

public class CookResponseDto {
  public String identifiantRecette;
  public String nomRecette;
  public List<IngredientRecommendationDto> ingredients;
  public List<String> ingredientsSansCorrespondance;

  public static class IngredientRecommendationDto {
    public String ingredientTexte;
    public List<RecommendedProductDto> produits;
  }

  public static class RecommendedProductDto {
    public String identifiant;
    public String nomProduit;
    public String marque;
    public String nutriScore;
    public Integer nova;
    public boolean produitDeBase;
    public double score;
  }
}
