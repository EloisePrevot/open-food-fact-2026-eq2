package ca.ulaval.glo4003.ws.api.data;

import ca.ulaval.glo4003.application.data.DataService;
import jakarta.ws.rs.core.Response;

public class DataResourceImpl implements DataResource {

  private final DataService dataService;

  public DataResourceImpl(DataService dataService) {
    this.dataService = dataService;
  }

  @Override
  public Response getExtractedData() {
    return Response.ok(dataService.getExtractedData()).build();
  }

  @Override
  public Response getTransformedData() {
    return Response.ok(dataService.getTransformedData()).build();
  }

  @Override
  public Response getRawData(String identifiant) {
    return Response.ok(dataService.getRawData(identifiant)).build();
  }
}
