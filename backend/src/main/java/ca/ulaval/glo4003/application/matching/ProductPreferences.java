package ca.ulaval.glo4003.application.matching;

import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import java.util.List;
import java.util.Optional;

/**
 * Hard filters applied to candidate products. A null preference means "no constraint". When a
 * preference is set, a product that cannot prove it satisfies the constraint (missing data) is
 * rejected, so the filter always reduces the result set.
 */
public final class ProductPreferences {

  private static final List<String> NUTRI_SCORE_ORDER = List.of("a", "b", "c", "d", "e");
  private static final int NOVA_MIN = 1;
  private static final int NOVA_MAX = 4;

  private final String marque;
  private final String nutriScoreMin;
  private final Integer novaMax;

  public ProductPreferences(String marque, String nutriScoreMin, Integer novaMax) {
    this.marque = normalize(marque);
    this.nutriScoreMin = validNutriScore(normalize(nutriScoreMin));
    this.novaMax = validNova(novaMax);
  }

  private static String validNutriScore(String nutriScore) {
    if (nutriScore != null && !NUTRI_SCORE_ORDER.contains(nutriScore.toLowerCase())) {
      throw new InvalidRequestException("nutriScoreMin doit être une lettre de A à E.");
    }
    return nutriScore;
  }

  private static Integer validNova(Integer nova) {
    if (nova != null && (nova < NOVA_MIN || nova > NOVA_MAX)) {
      throw new InvalidRequestException("novaMax doit être un entier de 1 à 4.");
    }
    return nova;
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
    return Optional.ofNullable(value)
        .map(String::strip)
        .filter(text -> !text.isEmpty())
        .orElse(null);
  }
}
