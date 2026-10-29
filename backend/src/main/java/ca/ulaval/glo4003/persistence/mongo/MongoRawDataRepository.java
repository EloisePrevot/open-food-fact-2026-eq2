package ca.ulaval.glo4003.persistence.mongo;

import static com.mongodb.client.model.Filters.eq;

import ca.ulaval.glo4003.application.data.RawDataRepository;
import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.Optional;
import org.bson.Document;
import org.bson.json.JsonWriterSettings;

public class MongoRawDataRepository implements RawDataRepository {

  private static final String IDENTIFIER_FIELD = "identifiant";
  private static final String SOURCE_FIELD = "source";
  private static final String INGESTION_DATE_FIELD = "dateIngestion";
  private static final String PAYLOAD_FIELD = "chargeUtile";

  private final MongoCollection<Document> rawData;

  public MongoRawDataRepository(PersistenceClients persistenceClients) {
    rawData = persistenceClients.mongoDatabase().getCollection(MongoCollections.RAW_DATA);
  }

  @Override
  public Optional<RawRecord> findByIdentifiant(String identifiant) {
    return Optional.ofNullable(rawData.find(eq("_id", identifiant)).first())
        .map(MongoRawDataRepository::toRawRecord);
  }

  private static RawRecord toRawRecord(Document document) {
    return new RawRecord(
        document.getString(IDENTIFIER_FIELD),
        DataSource.fromShortName(document.getString(SOURCE_FIELD)),
        document.getString(INGESTION_DATE_FIELD),
        payloadJson(document));
  }

  private static String payloadJson(Document document) {
    Object payload = document.get(PAYLOAD_FIELD);
    if (payload instanceof Document payloadDocument) {
      return payloadDocument.toJson(JsonWriterSettings.builder().build());
    }
    return new Document(PAYLOAD_FIELD, payload).toJson();
  }
}
