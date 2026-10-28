package ca.ulaval.glo4003.ws.api.shared;

import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class InvalidRequestExceptionMapper implements ExceptionMapper<InvalidRequestException> {

  @Override
  public Response toResponse(InvalidRequestException exception) {
    return Response.status(Response.Status.BAD_REQUEST)
        .type(MediaType.APPLICATION_JSON)
        .entity(Map.of("message", exception.getMessage()))
        .build();
  }
}
