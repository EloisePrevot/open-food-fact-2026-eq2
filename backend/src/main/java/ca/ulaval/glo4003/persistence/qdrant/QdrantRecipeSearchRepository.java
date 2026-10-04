package ca.ulaval.glo4003.persistence.qdrant;

import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.model.RecipeSearchDocument;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import io.qdrant.client.QdrantClient;
import java.util.List;

public class QdrantRecipeSearchRepository implements RecipeSearchRepository {
  private final QdrantClient qdrantClient;

  public QdrantRecipeSearchRepository(PersistenceClients persistenceClients) {
    qdrantClient = persistenceClients.qdrantClient();
  }

  @Override
  public void replaceAll(List<RecipeSearchDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
