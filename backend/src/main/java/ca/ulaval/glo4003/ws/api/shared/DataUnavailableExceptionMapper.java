package ca.ulaval.glo4003.ws.api.shared;

import ca.ulaval.glo4003.application.shared.DataUnavailableException;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class DataUnavailableExceptionMapper implements ExceptionMapper<DataUnavailableException> {

  private static final String MESSAGE =
      "%s : données pas encore disponibles, le chargement est peut-être en cours.";

  @Override
  public Response toResponse(DataUnavailableException exception) {
    return Response.status(Response.Status.SERVICE_UNAVAILABLE)
        .type(MediaType.APPLICATION_JSON)
        .entity(Map.of("message", MESSAGE.formatted(exception.getMessage())))
        .build();
  }
}
