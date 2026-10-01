package ca.ulaval.glo4003.ws.api.recipe;

import ca.ulaval.glo4003.ws.api.shared.NotImplementedResponse;
import jakarta.ws.rs.core.Response;

public class RecipeResourceImpl implements RecipeResource {

  @Override
  public Response getRecipeTypes() {
    return NotImplementedResponse.create();
  }

  @Override
  public Response searchRecipes(Object request) {
    return NotImplementedResponse.create();
  }

  @Override
  public Response cook(Object request) {
    return NotImplementedResponse.create();
  }
}
