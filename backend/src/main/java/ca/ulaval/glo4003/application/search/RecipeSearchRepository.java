package ca.ulaval.glo4003.application.search;

import ca.ulaval.glo4003.application.search.model.RecipeSearchDocument;
import ca.ulaval.glo4003.application.search.model.ScoredRecipe;
import java.util.List;
import java.util.Optional;

public interface RecipeSearchRepository {

  void replaceAll(List<RecipeSearchDocument> recipes);

  List<ScoredRecipe> searchSimilar(float[] vector, Optional<String> recipeType, int limit);
}
