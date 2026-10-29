package ca.ulaval.glo4003.application.matching;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.search.IngredientSearchRepository;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import ca.ulaval.glo4003.application.search.model.ScoredProduct;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchResponseDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchResponseDto.IngredientCandidateDto;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class IngredientMatchingServiceTest {

  private static final float[] VECTOR = {0.1f, 0.2f};
  private static final String INGREDIENT = "farine tout usage";
  private static final int LIMIT = 10;
  private static final int SEARCH_LIMIT = 50;

  private static final ProductDocument ENRICHED_FLOUR =
      new ProductDocument(
          "off:flour", "Farine blanche enrichie", false, "C", 4, List.of("Robin Hood"));
  private static final ProductDocument RAW_FLOUR =
      new ProductDocument("cnf:flour", "Farine de blé entier", true, null, null, List.of());

  private IngredientSearchRepository ingredientSearchRepository;
  private ProductRepository productRepository;
  private TextEmbedder textEmbedder;
  private IngredientMatchingService ingredientMatchingService;

  @BeforeEach
  void setUp() {
    ingredientSearchRepository = mock(IngredientSearchRepository.class);
    productRepository = mock(ProductRepository.class);
    textEmbedder = mock(TextEmbedder.class);
    ingredientMatchingService =
        new IngredientMatchingService(
            ingredientSearchRepository, productRepository, textEmbedder);
  }

  @Test
  void givenIngredient_whenMatching_thenCandidatesAreReturnedInSearchOrderWithScores() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.empty(), SEARCH_LIMIT))
        .thenReturn(
            List.of(
                new ScoredProduct("off:flour", 0.91, false),
                new ScoredProduct("cnf:flour", 0.72, true)));
    when(productRepository.findByIds(List.of("off:flour", "cnf:flour")))
        .thenReturn(List.of(RAW_FLOUR, ENRICHED_FLOUR));

    IngredientMatchResponseDto response =
        ingredientMatchingService.matchIngredient(request(INGREDIENT, null, LIMIT));

    assertThat(response.ingredient).isEqualTo(INGREDIENT);
    assertThat(response.candidats)
        .extracting(candidate -> candidate.identifiant)
        .containsExactly("off:flour", "cnf:flour");
    assertThat(response.candidats)
        .extracting(candidate -> candidate.score)
        .containsExactly(0.91, 0.72);
    assertThat(response.candidats)
        .extracting(candidate -> candidate.produitDeBase)
        .containsExactly(false, true);
  }

  @Test
  void givenIngredient_whenMatching_thenCandidatesCarryQualityIndicators() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.empty(), SEARCH_LIMIT))
        .thenReturn(
            List.of(
                new ScoredProduct("off:flour", 0.91, false),
                new ScoredProduct("cnf:flour", 0.72, true)));
    when(productRepository.findByIds(List.of("off:flour", "cnf:flour")))
        .thenReturn(List.of(ENRICHED_FLOUR, RAW_FLOUR));

    IngredientMatchResponseDto response =
        ingredientMatchingService.matchIngredient(request(INGREDIENT, null, LIMIT));

    IngredientCandidateDto branded = response.candidats.get(0);
    assertThat(branded.nutriScore).isEqualTo("C");
    assertThat(branded.nova).isEqualTo(4);
    assertThat(branded.marques).containsExactly("Robin Hood");

    IngredientCandidateDto missing = response.candidats.get(1);
    assertThat(missing.nutriScore).isNull();
    assertThat(missing.nova).isNull();
    assertThat(missing.marques).isEmpty();
  }

  @Test
  void givenBasicFoodFilter_whenMatching_thenFilterIsForwardedToSearch() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.of(true), SEARCH_LIMIT))
        .thenReturn(List.of(new ScoredProduct("cnf:flour", 0.72, true)));
    when(productRepository.findByIds(List.of("cnf:flour"))).thenReturn(List.of(RAW_FLOUR));

    IngredientMatchResponseDto response =
        ingredientMatchingService.matchIngredient(request(INGREDIENT, true, LIMIT));

    assertThat(response.candidats)
        .extracting(candidate -> candidate.nomProduit)
        .containsExactly("Farine de blé entier");
  }

  @Test
  void givenScoredProductMissingFromMongo_whenMatching_thenItIsDroppedFromCandidates() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.empty(), SEARCH_LIMIT))
        .thenReturn(
            List.of(
                new ScoredProduct("off:flour", 0.91, false),
                new ScoredProduct("off:missing", 0.5, false)));
    when(productRepository.findByIds(List.of("off:flour", "off:missing")))
        .thenReturn(List.of(ENRICHED_FLOUR));

    IngredientMatchResponseDto response =
        ingredientMatchingService.matchIngredient(request(INGREDIENT, null, LIMIT));

    assertThat(response.candidats)
        .extracting(candidate -> candidate.identifiant)
        .containsExactly("off:flour");
  }

  @Test
  void givenBrandQuery_whenSuggesting_thenRepositoryBrandsAreReturned() {
    when(productRepository.findBrands("gre", 10)).thenReturn(List.of("Great Value", "Green Giant"));

    assertThat(ingredientMatchingService.suggestBrands("gre", 10).marques)
        .containsExactly("Great Value", "Green Giant");
  }

  @Test
  void givenTooShortQuery_whenSuggesting_thenNoBrandsAreReturned() {
    assertThat(ingredientMatchingService.suggestBrands("g", 10).marques).isEmpty();

    verifyNoInteractions(productRepository);
  }

  @Test
  void givenNonPositiveLimit_whenSuggesting_thenDefaultLimitIsUsed() {
    when(productRepository.findBrands("great", 10)).thenReturn(List.of("Great Value"));

    assertThat(ingredientMatchingService.suggestBrands("great", 0).marques)
        .containsExactly("Great Value");
  }

  @Test
  void givenBlankIngredient_whenMatching_thenRequestIsRejected() {
    assertThatThrownBy(
            () -> ingredientMatchingService.matchIngredient(request("   ", null, LIMIT)))
        .isInstanceOf(InvalidRequestException.class);

    verifyNoInteractions(textEmbedder, ingredientSearchRepository, productRepository);
  }

  @Test
  void givenNonPositiveLimit_whenMatching_thenRequestIsRejected() {
    assertThatThrownBy(
            () -> ingredientMatchingService.matchIngredient(request(INGREDIENT, null, 0)))
        .isInstanceOf(InvalidRequestException.class);
  }

  @Test
  void givenNutriScoreMinFilter_whenMatching_thenProductsBelowThresholdAreExcluded() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.empty(), SEARCH_LIMIT))
        .thenReturn(
            List.of(
                new ScoredProduct("off:flour", 0.91, false),
                new ScoredProduct("cnf:flour", 0.72, true)));
    when(productRepository.findByIds(List.of("off:flour", "cnf:flour")))
        .thenReturn(List.of(ENRICHED_FLOUR, RAW_FLOUR));

    IngredientMatchRequestDto request = request(INGREDIENT, null, LIMIT);
    request.nutriScoreMin = "B";

    IngredientMatchResponseDto response = ingredientMatchingService.matchIngredient(request);

    assertThat(response.candidats).isEmpty();
  }

  @Test
  void givenMarqueFilter_whenMatching_thenOnlyMatchingBrandRemains() {
    when(textEmbedder.embed(INGREDIENT)).thenReturn(VECTOR);
    when(ingredientSearchRepository.searchSimilar(VECTOR, Optional.empty(), SEARCH_LIMIT))
        .thenReturn(
            List.of(
                new ScoredProduct("off:flour", 0.91, false),
                new ScoredProduct("cnf:flour", 0.72, true)));
    when(productRepository.findByIds(List.of("off:flour", "cnf:flour")))
        .thenReturn(List.of(ENRICHED_FLOUR, RAW_FLOUR));

    IngredientMatchRequestDto request = request(INGREDIENT, null, LIMIT);
    request.marque = "Robin Hood";

    IngredientMatchResponseDto response = ingredientMatchingService.matchIngredient(request);

    assertThat(response.candidats)
        .extracting(candidate -> candidate.identifiant)
        .containsExactly("off:flour");
  }

  private static IngredientMatchRequestDto request(
      String ingredient, Boolean produitDeBase, int limit) {
    IngredientMatchRequestDto request = new IngredientMatchRequestDto();
    request.ingredient = ingredient;
    request.produitDeBase = produitDeBase;
    request.limite = limit;
    return request;
  }
}
