package ca.ulaval.glo4003.ws.api.recipe;

import ca.ulaval.glo4003.ws.api.recipe.dto.CookRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import ca.ulaval.glo4003.ws.api.shared.NotImplementedResponse;
import jakarta.ws.rs.core.Response;

public class RecipeResourceImpl implements RecipeResource {

  @Override
  public Response getRecipeTypes() {
    return NotImplementedResponse.create();
  }

  @Override
  public Response searchRecipes(RecipeSearchRequestDto request) {
    return NotImplementedResponse.create();
  }

  @Override
  public Response cook(CookRequestDto request) {
    return NotImplementedResponse.create();
  }
}
