package ca.ulaval.glo4003.application.search;

import ca.ulaval.glo4003.application.search.model.IngredientSearchDocument;
import ca.ulaval.glo4003.application.search.model.ScoredProduct;
import java.util.List;
import java.util.Optional;

public interface IngredientSearchRepository {

  void replaceAll(List<IngredientSearchDocument> ingredients);

  List<ScoredProduct> searchSimilar(float[] vector, Optional<Boolean> produitDeBase, int limit);
}
