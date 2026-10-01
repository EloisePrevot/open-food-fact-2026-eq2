package ca.ulaval.glo4003.ws.api.matching.dto;

import java.util.List;

public class IngredientMatchResponseDto {
  public String ingredient;
  public List<IngredientCandidateDto> candidats;

  public static class IngredientCandidateDto {
    public String identifiant;
    public String nomProduit;
    public double score;
    public boolean produitDeBase;
  }
}
