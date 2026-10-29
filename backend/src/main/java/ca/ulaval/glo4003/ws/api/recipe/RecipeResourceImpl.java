package ca.ulaval.glo4003.ws.api.recipe;

import ca.ulaval.glo4003.application.recipes.RecipeService;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import jakarta.ws.rs.core.Response;

public class RecipeResourceImpl implements RecipeResource {

  private final RecipeService recipeService;

  public RecipeResourceImpl(RecipeService recipeService) {
    this.recipeService = recipeService;
  }

  @Override
  public Response getRecipeTypes() {
    return Response.ok(recipeService.getRecipeTypes()).build();
  }

  @Override
  public Response getRecipe(String identifiant) {
    return Response.ok(recipeService.getRecipe(identifiant)).build();
  }

  @Override
  public Response searchRecipes(RecipeSearchRequestDto request) {
    return Response.ok(recipeService.searchRecipes(request)).build();
  }

  @Override
  public Response cook(CookRequestDto request) {
    return Response.ok(recipeService.cook(request)).build();
  }
}
