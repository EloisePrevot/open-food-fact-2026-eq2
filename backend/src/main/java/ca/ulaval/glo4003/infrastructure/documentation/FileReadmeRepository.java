package ca.ulaval.glo4003.infrastructure.documentation;

import ca.ulaval.glo4003.application.documentation.ReadmeRepository;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class FileReadmeRepository implements ReadmeRepository {

  private final Path readmePath;

  public FileReadmeRepository(Path readmePath) {
    this.readmePath = readmePath;
  }

  @Override
  public String readReadme() {
    try {
      return Files.readString(readmePath, StandardCharsets.UTF_8);
    } catch (IOException exception) {
      throw new UncheckedIOException("README introuvable : " + readmePath, exception);
    }
  }
}
