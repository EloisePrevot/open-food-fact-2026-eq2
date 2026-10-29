package ca.ulaval.glo4003.application.data;

import ca.ulaval.glo4003.application.data.model.RawRecord;
import java.util.Optional;

public interface RawDataRepository {

  Optional<RawRecord> findByIdentifiant(String identifiant);
}
