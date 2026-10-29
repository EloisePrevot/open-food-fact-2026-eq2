package ca.ulaval.glo4003.persistence.mongo;

import static com.mongodb.client.model.Accumulators.first;
import static com.mongodb.client.model.Accumulators.sum;
import static com.mongodb.client.model.Aggregates.group;
import static com.mongodb.client.model.Aggregates.limit;
import static com.mongodb.client.model.Aggregates.match;
import static com.mongodb.client.model.Aggregates.sort;
import static com.mongodb.client.model.Aggregates.unwind;
import static com.mongodb.client.model.Filters.in;
import static com.mongodb.client.model.Filters.ne;
import static com.mongodb.client.model.Filters.regex;
import static com.mongodb.client.model.Projections.include;
import static com.mongodb.client.model.Sorts.descending;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.products.model.QualityIndicatorCounts;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import org.bson.Document;
import org.bson.conversions.Bson;

public class MongoProductRepository implements ProductRepository {

  private static final String NAME_FIELD = "nomProduit";
  private static final String BASIC_FOOD_FIELD = "produitDeBase";
  private static final String NUTRI_SCORE_FIELD = "nutriScore";
  private static final String NOVA_FIELD = "nova";
  private static final String BRANDS_FIELD = "marques";
  private static final String CATEGORY_FIELD = "categorie";
  private static final String COUNT_FIELD = "count";
  private static final Bson SUMMARY_FIELDS =
      include(NAME_FIELD, BASIC_FOOD_FIELD, NUTRI_SCORE_FIELD, NOVA_FIELD, BRANDS_FIELD);

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
    return products.find(in("_id", ids)).projection(SUMMARY_FIELDS).map(
            MongoProductRepository::toProduct)
        .into(new ArrayList<>());
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

  @Override
  public List<String> findBrands(String query, int limit) {
    Pattern pattern = caseInsensitiveContains(query);
    List<String> brands = new ArrayList<>();
    products
        .aggregate(
            List.of(
                // Leading $match on the collection so the multikey index on `marques` is used to
                // narrow documents before the array is unwound.
                match(regex(BRANDS_FIELD, pattern)),
                unwind("$" + BRANDS_FIELD),
                // Re-apply the filter to keep only the matching entries of each unwound array.
                match(regex(BRANDS_FIELD, pattern)),
                group("$" + BRANDS_FIELD, sum(COUNT_FIELD, 1)),
                sort(descending(COUNT_FIELD)),
                limit(limit)))
        .forEach(group -> brands.add(group.getString("_id")));
    return brands;
  }

  private static Pattern caseInsensitiveContains(String query) {
    return Pattern.compile(Pattern.quote(query.strip()), Pattern.CASE_INSENSITIVE);
  }

  private long countWithValue(String field) {
    return products.countDocuments(ne(field, null));
  }

  private static ProductDocument toProduct(Document document) {
    Number nova = document.get(NOVA_FIELD, Number.class);
    return new ProductDocument(
        document.getString("_id"),
        document.getString(NAME_FIELD),
        Boolean.TRUE.equals(document.getBoolean(BASIC_FOOD_FIELD)),
        document.getString(NUTRI_SCORE_FIELD),
        nova == null ? null : nova.intValue(),
        document.getList(BRANDS_FIELD, String.class, List.of()));
  }
}
