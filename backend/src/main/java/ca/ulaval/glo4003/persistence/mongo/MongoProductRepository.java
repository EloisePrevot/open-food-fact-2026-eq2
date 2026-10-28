package ca.ulaval.glo4003.persistence.mongo;

import static com.mongodb.client.model.Accumulators.sum;
import static com.mongodb.client.model.Aggregates.group;
import static com.mongodb.client.model.Aggregates.match;
import static com.mongodb.client.model.Aggregates.sort;
import static com.mongodb.client.model.Filters.ne;
import static com.mongodb.client.model.Sorts.descending;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.products.model.QualityIndicatorCounts;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.bson.Document;

public class MongoProductRepository implements ProductRepository {

  private static final String CATEGORY_FIELD = "categorie";
  private static final String COUNT_FIELD = "count";

  private final MongoCollection<Document> products;

  public MongoProductRepository(PersistenceClients persistenceClients) {
    products = persistenceClients.mongoDatabase().getCollection(MongoCollections.PRODUCTS);
  }

  @Override
  public void saveAll(List<ProductDocument> products) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<ProductDocument> findByIds(List<String> ids) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public QualityIndicatorCounts countQualityIndicators() {
    return new QualityIndicatorCounts(
        countWithValue("nutriScore"), countWithValue("nova"), countWithValue("ecoScore"));
  }

  @Override
  public Map<String, Long> countByCategory() {
    Map<String, Long> counts = new LinkedHashMap<>();
    products
        .aggregate(
            List.of(
                match(ne(CATEGORY_FIELD, null)),
                group("$" + CATEGORY_FIELD, sum(COUNT_FIELD, 1)),
                sort(descending(COUNT_FIELD))))
        .forEach(
            group ->
                counts.put(
                    group.getString("_id"), group.get(COUNT_FIELD, Number.class).longValue()));
    return counts;
  }

  private long countWithValue(String field) {
    return products.countDocuments(ne(field, null));
  }
}
