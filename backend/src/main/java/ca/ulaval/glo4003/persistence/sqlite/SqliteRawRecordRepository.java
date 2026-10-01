package ca.ulaval.glo4003.persistence.sqlite;

import ca.ulaval.glo4003.application.data.RawRecordRepository;
import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;

public class SqliteRawRecordRepository implements RawRecordRepository {

  @Override
  public void save(RawRecord rawRecord) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public java.util.Optional<RawRecord> findById(
      String id) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public long countBySource(DataSource source) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
