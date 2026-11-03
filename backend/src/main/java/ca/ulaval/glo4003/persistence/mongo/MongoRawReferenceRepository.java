package ca.ulaval.glo4003.persistence.mongo;

import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Projections.include;

import ca.ulaval.glo4003.application.data.RawReferenceRepository;
import ca.ulaval.glo4003.application.data.model.RawReference;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import org.bson.Document;

public class MongoRawReferenceRepository implements RawReferenceRepository {

  private static final String RAW_REFERENCE_FIELD = "refBrut";

  private final List<MongoCollection<Document>> collections;

  public MongoRawReferenceRepository(PersistenceClients persistenceClients) {
    collections =
        List.of(
            persistenceClients.mongoDatabase().getCollection(MongoCollections.PRODUCTS),
            persistenceClients.mongoDatabase().getCollection(MongoCollections.RECIPES));
  }

  @Override
  public Optional<RawReference> findByIdentifiant(String identifiant) {
    return collections.stream()
        .map(collection -> findRawReference(collection, identifiant))
        .filter(Objects::nonNull)
        .findFirst()
        .map(reference -> toRawReference(identifiant, reference));
  }

  private static Document findRawReference(MongoCollection<Document> collection, String id) {
    Document document =
        collection.find(eq("_id", id)).projection(include(RAW_REFERENCE_FIELD)).first();
    return document == null ? null : document.get(RAW_REFERENCE_FIELD, Document.class);
  }

  private static RawReference toRawReference(String identifiant, Document reference) {
    return new RawReference(
        identifiant,
        reference.get("artifactId", Number.class).longValue(),
        reference.get("ordinal", Number.class).longValue());
  }
}
