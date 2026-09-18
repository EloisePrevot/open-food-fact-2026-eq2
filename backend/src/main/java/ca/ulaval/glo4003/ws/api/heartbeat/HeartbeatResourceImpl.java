package ca.ulaval.glo4003.ws.api.heartbeat;

import ca.ulaval.glo4003.ws.api.heartbeat.dto.HeartbeatDto;

public class HeartbeatResourceImpl implements HeartbeatResource {

  private static final String NOM_APPLICATION = "Open Food Facts";

  @Override
  public HeartbeatDto getHeartbeat() {
    return new HeartbeatDto(NOM_APPLICATION);
  }
}
