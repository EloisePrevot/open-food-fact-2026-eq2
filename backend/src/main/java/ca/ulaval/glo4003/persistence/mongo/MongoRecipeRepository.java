package ca.ulaval.glo4003.persistence.mongo;

import ca.ulaval.glo4003.application.recipes.RecipeRepository;
import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import java.util.List;
import java.util.Optional;

public class MongoRecipeRepository implements RecipeRepository {

  @Override
  public void saveAll(List<RecipeDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public Optional<RecipeDocument> findById(String id) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<RecipeDocument> findByIds(List<String> ids) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<String> findTypes() {
    throw new UnsupportedOperationException("Not implemented");
  }
}
