package ca.ulaval.glo4003.ws.api.matching;

import ca.ulaval.glo4003.ws.api.matching.dto.ContainsRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchRequestDto;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/")
public interface IngredientMatchingResource {

  @POST
  @Path("/apparier_ingredient")
  @Consumes(MediaType.APPLICATION_JSON)
  @Produces(MediaType.APPLICATION_JSON)
  Response matchIngredient(IngredientMatchRequestDto request);

  @POST
  @Path("/contient")
  @Consumes(MediaType.APPLICATION_JSON)
  @Produces(MediaType.APPLICATION_JSON)
  Response findProductsContainingIngredient(ContainsRequestDto request);
}
