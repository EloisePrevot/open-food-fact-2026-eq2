package ca.ulaval.glo4003.application.shared;

public class NotImplementedException extends RuntimeException {

  private static final long serialVersionUID = 1L;

  public NotImplementedException() {
    super("Not implemented");
  }
}
