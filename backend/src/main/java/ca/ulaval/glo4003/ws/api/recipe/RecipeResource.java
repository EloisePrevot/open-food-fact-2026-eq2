package ca.ulaval.glo4003.ws.api.recipe;

import ca.ulaval.glo4003.ws.api.recipe.dto.CookRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/")
public interface RecipeResource {

  @GET
  @Path("/type")
  @Produces(MediaType.APPLICATION_JSON)
  Response getRecipeTypes();

  @POST
  @Path("/recette")
  @Consumes(MediaType.APPLICATION_JSON)
  @Produces(MediaType.APPLICATION_JSON)
  Response searchRecipes(RecipeSearchRequestDto request);

  @POST
  @Path("/cuisiner")
  @Consumes(MediaType.APPLICATION_JSON)
  @Produces(MediaType.APPLICATION_JSON)
  Response cook(CookRequestDto request);
}
