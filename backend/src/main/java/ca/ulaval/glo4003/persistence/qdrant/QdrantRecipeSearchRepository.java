package ca.ulaval.glo4003.persistence.qdrant;

import static io.qdrant.client.ConditionFactory.matchKeyword;
import static io.qdrant.client.QueryFactory.nearest;
import static io.qdrant.client.WithPayloadSelectorFactory.include;

import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.model.RecipeSearchDocument;
import ca.ulaval.glo4003.application.search.model.ScoredRecipe;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceException;
import io.qdrant.client.QdrantClient;
import io.qdrant.client.grpc.Common.Filter;
import io.qdrant.client.grpc.Points.QueryPoints;
import io.qdrant.client.grpc.Points.ScoredPoint;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ExecutionException;

public class QdrantRecipeSearchRepository implements RecipeSearchRepository {

  private static final String COLLECTION_NAME = "recipes";
  private static final String IDENTIFIER_FIELD = "identifiant";
  private static final String TYPE_FIELD = "type";

  private final QdrantClient qdrantClient;

  public QdrantRecipeSearchRepository(PersistenceClients persistenceClients) {
    qdrantClient = persistenceClients.qdrantClient();
  }

  @Override
  public void replaceAll(List<RecipeSearchDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<ScoredRecipe> searchSimilar(float[] vector, Optional<String> recipeType, int limit) {
    try {
      return qdrantClient.queryAsync(query(vector, recipeType, limit)).get().stream()
          .map(QdrantRecipeSearchRepository::toScoredRecipe)
          .toList();
    } catch (ExecutionException exception) {
      throw new PersistenceException("Recherche Qdrant impossible", exception);
    } catch (InterruptedException exception) {
      Thread.currentThread().interrupt();
      throw new PersistenceException("Recherche Qdrant interrompue", exception);
    }
  }

  private static QueryPoints query(float[] vector, Optional<String> recipeType, int limit) {
    QueryPoints.Builder query =
        QueryPoints.newBuilder()
            .setCollectionName(COLLECTION_NAME)
            .setQuery(nearest(vector))
            .setLimit(limit)
            .setWithPayload(include(List.of(IDENTIFIER_FIELD)));
    recipeType.ifPresent(
        type -> query.setFilter(Filter.newBuilder().addMust(matchKeyword(TYPE_FIELD, type))));
    return query.build();
  }

  private static ScoredRecipe toScoredRecipe(ScoredPoint point) {
    return new ScoredRecipe(
        point.getPayloadMap().get(IDENTIFIER_FIELD).getStringValue(), point.getScore());
  }
}
