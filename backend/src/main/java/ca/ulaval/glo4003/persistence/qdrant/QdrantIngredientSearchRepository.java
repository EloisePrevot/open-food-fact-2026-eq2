package ca.ulaval.glo4003.persistence.qdrant;

import ca.ulaval.glo4003.application.search.IngredientSearchRepository;
import ca.ulaval.glo4003.application.search.model.IngredientSearchDocument;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import io.qdrant.client.QdrantClient;
import java.util.List;

public class QdrantIngredientSearchRepository implements IngredientSearchRepository {
  private final QdrantClient qdrantClient;

  public QdrantIngredientSearchRepository(PersistenceClients persistenceClients) {
    qdrantClient = persistenceClients.qdrantClient();
  }

  @Override
  public void replaceAll(List<IngredientSearchDocument> ingredients) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
