package ca.ulaval.glo4003.ws.api.documentation;

import ca.ulaval.glo4003.application.documentation.DocumentationService;
import jakarta.ws.rs.core.Response;

public class DocumentationResourceImpl implements DocumentationResource {

  private final DocumentationService documentationService;

  public DocumentationResourceImpl(DocumentationService documentationService) {
    this.documentationService = documentationService;
  }

  @Override
  public Response getReadme() {
    return Response.ok(documentationService.getReadme()).build();
  }
}
