package ca.ulaval.glo4003.ws.api.heartbeat;

import ca.ulaval.glo4003.ws.api.heartbeat.dto.HeartbeatDto;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/heartbeat")
public interface HeartbeatResource {

  @GET
  @Produces(MediaType.APPLICATION_JSON)
  HeartbeatDto getHeartbeat();
}
