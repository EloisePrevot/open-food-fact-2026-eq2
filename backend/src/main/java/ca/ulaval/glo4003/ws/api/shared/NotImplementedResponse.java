package ca.ulaval.glo4003.ws.api.shared;

import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.util.Map;

public final class NotImplementedResponse {

  private static final Map<String, String> RESPONSE_BODY = Map.of("message", "Not implemented");

  private NotImplementedResponse() {}

  public static Response create() {
    return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
        .type(MediaType.APPLICATION_JSON)
        .entity(RESPONSE_BODY)
        .build();
  }
}
