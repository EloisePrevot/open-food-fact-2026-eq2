package ca.ulaval.glo4003.persistence.mongo;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.List;
import org.bson.Document;

public class MongoProductRepository implements ProductRepository {
  private static final String COLLECTION_NAME = "produits";

  private final MongoCollection<Document> products;

  public MongoProductRepository(PersistenceClients persistenceClients) {
    products = persistenceClients.mongoDatabase().getCollection(COLLECTION_NAME);
  }

  @Override
  public void saveAll(List<ProductDocument> products) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<ProductDocument> findByIds(List<String> ids) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
