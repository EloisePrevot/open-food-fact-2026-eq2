package ca.ulaval.glo4003.ws.api.matching;

import ca.ulaval.glo4003.application.matching.IngredientMatchingService;
import ca.ulaval.glo4003.ws.api.matching.dto.ContainsRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchRequestDto;
import jakarta.ws.rs.core.Response;

public class IngredientMatchingResourceImpl implements IngredientMatchingResource {

  private final IngredientMatchingService ingredientMatchingService;

  public IngredientMatchingResourceImpl(IngredientMatchingService ingredientMatchingService) {
    this.ingredientMatchingService = ingredientMatchingService;
  }

  @Override
  public Response matchIngredient(IngredientMatchRequestDto request) {
    return Response.ok(ingredientMatchingService.matchIngredient(request)).build();
  }

  @Override
  public Response findProductsContainingIngredient(ContainsRequestDto request) {
    return Response.ok(ingredientMatchingService.findProductsContainingIngredient(request)).build();
  }
}
