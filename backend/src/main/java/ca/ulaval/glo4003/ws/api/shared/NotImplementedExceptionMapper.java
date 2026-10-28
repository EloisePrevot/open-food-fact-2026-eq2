package ca.ulaval.glo4003.ws.api.shared;

import ca.ulaval.glo4003.application.shared.NotImplementedException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;

@Provider
public class NotImplementedExceptionMapper implements ExceptionMapper<NotImplementedException> {

  @Override
  public Response toResponse(NotImplementedException exception) {
    return NotImplementedResponse.create();
  }
}
