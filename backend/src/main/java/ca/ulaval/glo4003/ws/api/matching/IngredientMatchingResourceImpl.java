package ca.ulaval.glo4003.ws.api.matching;

import ca.ulaval.glo4003.ws.api.matching.dto.ContainsRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchRequestDto;
import ca.ulaval.glo4003.ws.api.shared.NotImplementedResponse;
import jakarta.ws.rs.core.Response;

public class IngredientMatchingResourceImpl implements IngredientMatchingResource {

  @Override
  public Response matchIngredient(IngredientMatchRequestDto request) {
    return NotImplementedResponse.create();
  }

  @Override
  public Response findProductsContainingIngredient(ContainsRequestDto request) {
    return NotImplementedResponse.create();
  }
}
