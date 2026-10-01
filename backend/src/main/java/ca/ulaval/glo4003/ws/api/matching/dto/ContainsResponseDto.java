package ca.ulaval.glo4003.ws.api.matching.dto;

import java.util.List;

public class ContainsResponseDto {
  public String ingredient;
  public List<ContainingProductDto> produits;
  public List<SubstituteProductDto> substituts;

  public static class ContainingProductDto {
    public String identifiant;
    public String nomProduit;
    public int profondeur;
    public List<String> chemin;
  }

  public static class SubstituteProductDto {
    public String identifiant;
    public String nomProduit;
    public String categorie;
  }
}
