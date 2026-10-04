package ca.ulaval.glo4003.ws.api.data;

import ca.ulaval.glo4003.ws.api.shared.NotImplementedResponse;
import jakarta.ws.rs.core.Response;

public class DataResourceImpl implements DataResource {

  @Override
  public Response getExtractedData() {
    return NotImplementedResponse.create();
  }

  @Override
  public Response getTransformedData() {
    return NotImplementedResponse.create();
  }

  @Override
  public Response getRawData(String identifiant) {
    return NotImplementedResponse.create();
  }
}
