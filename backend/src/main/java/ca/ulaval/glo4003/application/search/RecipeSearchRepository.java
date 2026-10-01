package ca.ulaval.glo4003.application.search;

import ca.ulaval.glo4003.application.search.model.RecipeSearchDocument;
import java.util.List;

public interface RecipeSearchRepository {

  void replaceAll(List<RecipeSearchDocument> recipes);
}
