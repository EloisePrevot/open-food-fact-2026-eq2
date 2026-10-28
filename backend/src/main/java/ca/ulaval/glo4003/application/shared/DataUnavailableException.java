package ca.ulaval.glo4003.application.shared;

public class DataUnavailableException extends RuntimeException {

  private static final long serialVersionUID = 1L;

  public DataUnavailableException(String message, Throwable cause) {
    super(message, cause);
  }
}
