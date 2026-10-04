package ca.ulaval.glo4003.application.recipes;

import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import java.util.List;
import java.util.Optional;

public interface RecipeRepository {

  void saveAll(List<RecipeDocument> recipes);

  Optional<RecipeDocument> findById(String id);

  List<RecipeDocument> findByIds(List<String> ids);

  List<String> findTypes();
}
