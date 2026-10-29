package ca.ulaval.glo4003.persistence.qdrant;

import static io.qdrant.client.ConditionFactory.match;
import static io.qdrant.client.QueryFactory.nearest;
import static io.qdrant.client.WithPayloadSelectorFactory.include;

import ca.ulaval.glo4003.application.search.IngredientSearchRepository;
import ca.ulaval.glo4003.application.search.model.IngredientSearchDocument;
import ca.ulaval.glo4003.application.search.model.ScoredProduct;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceException;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Common.Filter;
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

public class QdrantIngredientSearchRepository implements IngredientSearchRepository {

  private static final String COLLECTION_NAME = "ingredients";
  private static final String IDENTIFIER_FIELD = "identifiant";
  private static final String BASIC_FOOD_FIELD = "produitDeBase";

  private final QdrantClient qdrantClient;

  public QdrantIngredientSearchRepository(PersistenceClients persistenceClients) {
    qdrantClient = persistenceClients.qdrantClient();
  }

  @Override
  public void replaceAll(List<IngredientSearchDocument> ingredients) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<ScoredProduct> searchSimilar(
      float[] vector, Optional<Boolean> produitDeBase, int limit) {
    try {
      return qdrantClient.queryAsync(query(vector, produitDeBase, limit)).get().stream()
          .map(QdrantIngredientSearchRepository::toScoredProduct)
          .toList();
    } catch (ExecutionException exception) {
      throw new PersistenceException("Recherche Qdrant impossible", exception);
    } catch (InterruptedException exception) {
      Thread.currentThread().interrupt();
      throw new PersistenceException("Recherche Qdrant interrompue", exception);
    }
  }

  private static QueryPoints query(float[] vector, Optional<Boolean> produitDeBase, int limit) {
    QueryPoints.Builder query =
        QueryPoints.newBuilder()
            .setCollectionName(COLLECTION_NAME)
            .setQuery(nearest(vector))
            .setLimit(limit)
            .setWithPayload(include(List.of(IDENTIFIER_FIELD, BASIC_FOOD_FIELD)));
    produitDeBase.ifPresent(
        basicFood ->
            query.setFilter(Filter.newBuilder().addMust(match(BASIC_FOOD_FIELD, basicFood))));
    return query.build();
  }

  private static ScoredProduct toScoredProduct(ScoredPoint point) {
    return new ScoredProduct(
        point.getPayloadMap().get(IDENTIFIER_FIELD).getStringValue(),
        point.getScore(),
        point.getPayloadMap().get(BASIC_FOOD_FIELD).getBoolValue());
  }
}
