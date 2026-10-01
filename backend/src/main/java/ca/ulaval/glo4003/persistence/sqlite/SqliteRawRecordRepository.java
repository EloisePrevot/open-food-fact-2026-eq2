package ca.ulaval.glo4003.persistence.sqlite;

import ca.ulaval.glo4003.application.data.RawRecordRepository;
import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.Optional;

public class SqliteRawRecordRepository implements RawRecordRepository {
  private final PersistenceClients persistenceClients;

  public SqliteRawRecordRepository(PersistenceClients persistenceClients) {
    this.persistenceClients = persistenceClients;
  }

  @Override
  public void save(RawRecord rawRecord) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public Optional<RawRecord> findById(String id) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public long countBySource(DataSource source) {
    throw new UnsupportedOperationException("Not implemented");
  }

  Connection openConnection() throws SQLException {
    return persistenceClients.openSqliteConnection();
  }
}
