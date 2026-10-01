package ca.ulaval.glo4003.ws.api.matching;

import ca.ulaval.glo4003.ws.api.shared.NotImplementedResponse;
import jakarta.ws.rs.core.Response;

public class IngredientMatchingResourceImpl implements IngredientMatchingResource {

  @Override
  public Response matchIngredient(Object request) {
    return NotImplementedResponse.create();
  }

  @Override
  public Response findProductsContainingIngredient(Object request) {
    return NotImplementedResponse.create();
  }
}
