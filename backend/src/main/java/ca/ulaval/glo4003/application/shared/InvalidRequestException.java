package ca.ulaval.glo4003.application.shared;

public class InvalidRequestException extends RuntimeException {

  private static final long serialVersionUID = 1L;

  public InvalidRequestException(String message) {
    super(message);
  }
}
