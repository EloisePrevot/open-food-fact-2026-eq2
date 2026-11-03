package ca.ulaval.glo4003.application.documentation;

public class DocumentationService {

  private final ReadmeRepository readmeRepository;

  public DocumentationService(ReadmeRepository readmeRepository) {
    this.readmeRepository = readmeRepository;
  }

  public String getReadme() {
    return readmeRepository.readReadme();
  }
}
