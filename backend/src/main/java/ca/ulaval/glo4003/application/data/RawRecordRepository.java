package ca.ulaval.glo4003.application.data;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import java.util.Optional;

public interface RawRecordRepository {

  void save(RawRecord rawRecord);

  Optional<RawRecord> findById(String id);

  long countBySource(DataSource source);
}
