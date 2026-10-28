package ca.ulaval.glo4003.ws.api.data.dto;

import com.fasterxml.jackson.annotation.JsonRawValue;

public class RawDataDto {
  public String identifiant;
  public String source;
  public String dateIngestion;
  @JsonRawValue public String chargeUtile;
}
