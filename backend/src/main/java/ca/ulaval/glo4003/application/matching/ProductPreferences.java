package ca.ulaval.glo4003.application.matching;

import ca.ulaval.glo4003.application.products.model.ProductDocument;
import java.util.List;
import java.util.Optional;

/**
 * Hard filters applied to candidate products. A null preference means "no constraint". When a
 * preference is set, a product that cannot prove it satisfies the constraint (missing data) is
 * rejected, so the filter always reduces the result set.
 */
public final class ProductPreferences {

  private static final List<String> NUTRI_SCORE_ORDER = List.of("a", "b", "c", "d", "e");

  private final String marque;
  private final String nutriScoreMin;
  private final Integer novaMax;

  public ProductPreferences(String marque, String nutriScoreMin, Integer novaMax) {
    this.marque = normalize(marque);
    this.nutriScoreMin = normalize(nutriScoreMin);
    this.novaMax = novaMax;
  }

  public boolean accepts(ProductDocument product) {
    return matchesMarque(product) && matchesNutriScore(product) && matchesNova(product);
  }

  private boolean matchesMarque(ProductDocument product) {
    if (marque == null) {
      return true;
    }
    return product.marques().stream().anyMatch(brand -> marque.equalsIgnoreCase(brand.strip()));
  }

  private boolean matchesNutriScore(ProductDocument product) {
    if (nutriScoreMin == null) {
      return true;
    }
    int threshold = NUTRI_SCORE_ORDER.indexOf(nutriScoreMin.toLowerCase());
    return rank(product.nutriScore()).map(rank -> rank <= threshold).orElse(false);
  }

  private boolean matchesNova(ProductDocument product) {
    if (novaMax == null) {
      return true;
    }
    return product.nova() != null && product.nova() <= novaMax;
  }

  private static Optional<Integer> rank(String nutriScore) {
    if (nutriScore == null) {
      return Optional.empty();
    }
    int rank = NUTRI_SCORE_ORDER.indexOf(nutriScore.toLowerCase());
    return rank < 0 ? Optional.empty() : Optional.of(rank);
  }

  private static String normalize(String value) {
    return Optional.ofNullable(value).map(String::strip).filter(text -> !text.isEmpty()).orElse(null);
  }
}
