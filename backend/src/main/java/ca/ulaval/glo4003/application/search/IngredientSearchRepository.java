package ca.ulaval.glo4003.application.search;

import ca.ulaval.glo4003.application.search.model.IngredientSearchDocument;
import java.util.List;

public interface IngredientSearchRepository {

  void replaceAll(List<IngredientSearchDocument> ingredients);
}
