package ca.ulaval.glo4003.application.matching;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import java.util.List;
import org.junit.jupiter.api.Test;

class ProductPreferencesTest {

  private static final ProductPreferences NO_PREFERENCE = new ProductPreferences(null, null, null);

  private static ProductDocument product(String nutriScore, Integer nova, List<String> marques) {
    return new ProductDocument("off:1", "Produit", false, nutriScore, nova, marques);
  }

  @Test
  void givenNoPreference_thenEveryProductIsAccepted() {
    assertThat(NO_PREFERENCE.accepts(product(null, null, List.of()))).isTrue();
  }

  @Test
  void givenNutriScoreMin_thenBetterOrEqualGradesAreAccepted() {
    ProductPreferences preferences = new ProductPreferences(null, "B", null);

    assertThat(preferences.accepts(product("a", null, List.of()))).isTrue();
    assertThat(preferences.accepts(product("b", null, List.of()))).isTrue();
    assertThat(preferences.accepts(product("c", null, List.of()))).isFalse();
  }

  @Test
  void givenNutriScoreMin_whenNutriScoreMissing_thenProductIsRejected() {
    ProductPreferences preferences = new ProductPreferences(null, "C", null);

    assertThat(preferences.accepts(product(null, null, List.of()))).isFalse();
  }

  @Test
  void givenNovaMax_thenLowerOrEqualClassificationsAreAccepted() {
    ProductPreferences preferences = new ProductPreferences(null, null, 2);

    assertThat(preferences.accepts(product(null, 1, List.of()))).isTrue();
    assertThat(preferences.accepts(product(null, 2, List.of()))).isTrue();
    assertThat(preferences.accepts(product(null, 3, List.of()))).isFalse();
  }

  @Test
  void givenNovaMax_whenNovaMissing_thenProductIsRejected() {
    ProductPreferences preferences = new ProductPreferences(null, null, 3);

    assertThat(preferences.accepts(product(null, null, List.of()))).isFalse();
  }

  @Test
  void givenMarque_thenOnlyMatchingBrandIsAccepted() {
    ProductPreferences preferences = new ProductPreferences("Bonduelle", null, null);

    assertThat(preferences.accepts(product(null, null, List.of("Bonduelle")))).isTrue();
    assertThat(preferences.accepts(product(null, null, List.of("Autre")))).isFalse();
    assertThat(preferences.accepts(product(null, null, List.of()))).isFalse();
  }

  @Test
  void givenBlankNutriScoreMin_thenNoNutriScoreFilterIsApplied() {
    ProductPreferences preferences = new ProductPreferences(null, "  ", null);

    assertThat(preferences.accepts(product(null, null, List.of()))).isTrue();
  }

  @Test
  void givenNutriScoreMinOutsideAToE_thenRequestIsRejected() {
    assertThatThrownBy(() -> new ProductPreferences(null, "Z", null))
        .isInstanceOf(InvalidRequestException.class);
  }

  @Test
  void givenNovaMaxBelowOne_thenRequestIsRejected() {
    assertThatThrownBy(() -> new ProductPreferences(null, null, 0))
        .isInstanceOf(InvalidRequestException.class);
  }

  @Test
  void givenNovaMaxAboveFour_thenRequestIsRejected() {
    assertThatThrownBy(() -> new ProductPreferences(null, null, 5))
        .isInstanceOf(InvalidRequestException.class);
  }

  @Test
  void givenMultipleFilters_thenAllMustBeSatisfied() {
    ProductPreferences preferences = new ProductPreferences("Bonduelle", "B", 2);

    assertThat(preferences.accepts(product("a", 1, List.of("Bonduelle")))).isTrue();
    assertThat(preferences.accepts(product("d", 1, List.of("Bonduelle")))).isFalse();
  }
}
