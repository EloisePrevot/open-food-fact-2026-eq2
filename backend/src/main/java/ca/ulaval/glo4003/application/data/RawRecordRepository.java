package ca.ulaval.glo4003.application.data;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.data.model.RawReference;
import java.util.Optional;

public interface RawRecordRepository {

  Optional<RawRecord> findByReference(RawReference reference);

  long countBySource(DataSource source);
}
