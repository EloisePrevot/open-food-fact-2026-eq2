package ca.ulaval.glo4003.ws.api.data;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/")
public interface DataResource {

  @GET
  @Path("/extracted_data")
  @Produces(MediaType.APPLICATION_JSON)
  Response getExtractedData();

  @GET
  @Path("/transformed_data")
  @Produces(MediaType.APPLICATION_JSON)
  Response getTransformedData();

  @GET
  @Path("/donnees_brutes/{identifiant}")
  @Produces(MediaType.APPLICATION_JSON)
  Response getRawData(@PathParam("identifiant") String identifiant);
}
