package ca.ulaval.glo4003.application.data;

import ca.ulaval.glo4003.application.data.model.RawReference;
import java.util.Optional;

public interface RawReferenceRepository {

  Optional<RawReference> findByIdentifiant(String identifiant);
}
