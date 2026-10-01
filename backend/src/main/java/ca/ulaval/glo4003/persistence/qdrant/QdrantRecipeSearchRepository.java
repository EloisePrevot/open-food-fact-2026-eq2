package ca.ulaval.glo4003.persistence.qdrant;

import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.model.RecipeSearchDocument;
import java.util.List;

public class QdrantRecipeSearchRepository implements RecipeSearchRepository {

  @Override
  public void replaceAll(List<RecipeSearchDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
