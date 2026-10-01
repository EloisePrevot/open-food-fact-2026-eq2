package ca.ulaval.glo4003.ws.api.documentation;

import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

public class DocumentationResourceImpl implements DocumentationResource {

  private static final String NOT_IMPLEMENTED_MESSAGE = "Not implemented";

  @Override
  public Response getReadme() {
    return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
        .type(MediaType.TEXT_PLAIN)
        .entity(NOT_IMPLEMENTED_MESSAGE)
        .build();
  }
}
