package ca.ulaval.glo4003.persistence;

import ca.ulaval.glo4003.application.shared.DataUnavailableException;

public class PersistenceException extends DataUnavailableException {

  private static final long serialVersionUID = 1L;

  public PersistenceException(String message, Throwable cause) {
    super(message, cause);
  }
}
