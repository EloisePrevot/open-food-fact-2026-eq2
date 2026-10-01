package ca.ulaval.glo4003.persistence.qdrant;

import ca.ulaval.glo4003.application.search.IngredientSearchRepository;
import ca.ulaval.glo4003.application.search.model.IngredientSearchDocument;
import java.util.List;

public class QdrantIngredientSearchRepository implements IngredientSearchRepository {

  @Override
  public void replaceAll(List<IngredientSearchDocument> ingredients) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
