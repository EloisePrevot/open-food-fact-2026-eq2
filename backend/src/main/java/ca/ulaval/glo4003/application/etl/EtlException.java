package ca.ulaval.glo4003.application.etl;

public class EtlException extends RuntimeException {

  private static final long serialVersionUID = 1L;

  public EtlException(String message) {
    super(message);
  }

  public EtlException(String message, Throwable cause) {
    super(message, cause);
  }
}
