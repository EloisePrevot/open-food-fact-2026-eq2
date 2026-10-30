package ca.ulaval.glo4003.application.recipes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import ca.ulaval.glo4003.application.matching.IngredientMatchingService;
import ca.ulaval.glo4003.application.matching.ProductPreferences;
import ca.ulaval.glo4003.application.matching.ScoredProductDocument;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.recipes.model.RecipeDetailDocument;
import ca.ulaval.glo4003.application.recipes.model.RecipeDetailDocument.RecipeIngredient;
import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import ca.ulaval.glo4003.application.search.model.ScoredRecipe;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import ca.ulaval.glo4003.application.shared.NotFoundException;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookResponseDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeDetailDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchResponseDto.RecipeSummaryDto;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class RecipeServiceTest {

  private static final float[] VECTOR = {0.1f, 0.2f};
  private static final RecipeDocument SOUP =
      new RecipeDocument("recipe:soup", "Soup", List.of("soup"), 5);
  private static final RecipeDocument STEW =
      new RecipeDocument("recipe:stew", "Stew", List.of("main"), 8);

  private RecipeRepository recipeRepository;
  private RecipeSearchRepository recipeSearchRepository;
  private IngredientMatchingService ingredientMatchingService;
  private TextEmbedder textEmbedder;
  private RecipeService recipeService;

  @BeforeEach
  void setUp() {
    recipeRepository = mock(RecipeRepository.class);
    recipeSearchRepository = mock(RecipeSearchRepository.class);
    ingredientMatchingService = mock(IngredientMatchingService.class);
    textEmbedder = mock(TextEmbedder.class);
    recipeService =
        new RecipeService(
            recipeRepository, recipeSearchRepository, ingredientMatchingService, textEmbedder);
  }

  @Test
  void whenGettingTypes_thenRepositoryTypesAreReturned() {
    when(recipeRepository.findTypes()).thenReturn(List.of("main", "soup"));

    assertThat(recipeService.getRecipeTypes().typesRecette).containsExactly("main", "soup");
  }

  @Test
  void givenNoDescription_whenSearching_thenRecipesOfTypeAreReturnedWithoutScore() {
    when(recipeRepository.findFirst(Optional.of("soup"), 10)).thenReturn(List.of(SOUP));

    List<RecipeSummaryDto> recipes =
        recipeService.searchRecipes(request("soup", "  ", 10)).recettes;

    assertThat(recipes).extracting(recipe -> recipe.identifiant).containsExactly("recipe:soup");
    assertThat(recipes.get(0).score).isNull();
    verifyNoInteractions(textEmbedder, recipeSearchRepository);
  }

  @Test
  void givenDescription_whenSearching_thenRecipesAreOrderedBySimilarity() {
    when(textEmbedder.embed("souper d'hiver")).thenReturn(VECTOR);
    when(recipeSearchRepository.searchSimilar(VECTOR, Optional.empty(), 2))
        .thenReturn(
            List.of(new ScoredRecipe("recipe:stew", 0.9), new ScoredRecipe("recipe:soup", 0.7)));
    when(recipeRepository.findByIds(List.of("recipe:stew", "recipe:soup")))
        .thenReturn(List.of(SOUP, STEW));

    List<RecipeSummaryDto> recipes =
        recipeService.searchRecipes(request(null, "souper d'hiver", 2)).recettes;

    assertThat(recipes)
        .extracting(recipe -> recipe.identifiant)
        .containsExactly("recipe:stew", "recipe:soup");
    assertThat(recipes).extracting(recipe -> recipe.score).containsExactly(0.9, 0.7);
  }

  @Test
  void givenKnownIdentifier_whenGettingRecipe_thenDetailIsReturned() {
    RecipeDetailDocument detail =
        new RecipeDetailDocument(
            "recipe:soup",
            "Soup",
            "A warm soup",
            List.of("soup"),
            List.of(new RecipeIngredient("carrot", "carrot", "2 carrots")),
            List.of("Chop the carrots.", "Simmer."));
    when(recipeRepository.findDetailById("recipe:soup")).thenReturn(Optional.of(detail));

    RecipeDetailDto result = recipeService.getRecipe("recipe:soup");

    assertThat(result.nom).isEqualTo("Soup");
    assertThat(result.description).isEqualTo("A warm soup");
    assertThat(result.etapes).containsExactly("Chop the carrots.", "Simmer.");
    assertThat(result.ingredients)
        .extracting(ingredient -> ingredient.cle)
        .containsExactly("carrot");
  }

  @Test
  void givenUnknownIdentifier_whenGettingRecipe_thenNotFoundIsThrown() {
    when(recipeRepository.findDetailById("recipe:missing")).thenReturn(Optional.empty());

    assertThatThrownBy(() -> recipeService.getRecipe("recipe:missing"))
        .isInstanceOf(NotFoundException.class);
  }

  @Test
  void givenNonPositiveLimit_whenSearching_thenRequestIsRejected() {
    assertThatThrownBy(() -> recipeService.searchRecipes(request(null, null, 0)))
        .isInstanceOf(InvalidRequestException.class);
  }

  @Test
  void givenRecipe_whenCooking_thenEachIngredientGetsFilteredRecommendations() {
    RecipeDetailDocument detail =
        new RecipeDetailDocument(
            "recipe:soup",
            "Soup",
            "A warm soup",
            List.of("soup"),
            List.of(
                new RecipeIngredient("carrot", "carrot", "2 carrots"),
                new RecipeIngredient("salt", "salt", "a pinch of salt")),
            List.of("Chop.", "Simmer."));
    when(recipeRepository.findDetailById("recipe:soup")).thenReturn(Optional.of(detail));
    ProductDocument carrotProduct =
        new ProductDocument("off:carrot", "Carottes bio", false, "A", 1, List.of("Bonduelle"));
    when(ingredientMatchingService.recommendProducts(
            eq("carrot"), any(ProductPreferences.class), eq(Optional.empty()), eq(3)))
        .thenReturn(List.of(new ScoredProductDocument(0.95, carrotProduct)));
    when(ingredientMatchingService.recommendProducts(
            eq("salt"), any(ProductPreferences.class), eq(Optional.empty()), eq(3)))
        .thenReturn(List.of());

    CookResponseDto response = recipeService.cook(cookRequest("recipe:soup", 3));

    assertThat(response.nomRecette).isEqualTo("Soup");
    assertThat(response.ingredients)
        .extracting(recommendation -> recommendation.ingredientTexte)
        .containsExactly("2 carrots");
    assertThat(response.ingredients.get(0).produits)
        .extracting(product -> product.nutriScore)
        .containsExactly("A");
    assertThat(response.ingredients.get(0).produits)
        .extracting(product -> product.marque)
        .containsExactly("Bonduelle");
    assertThat(response.ingredientsSansCorrespondance).containsExactly("a pinch of salt");
  }

  @Test
  void givenUnknownRecipe_whenCooking_thenNotFoundIsThrown() {
    when(recipeRepository.findDetailById("recipe:missing")).thenReturn(Optional.empty());

    assertThatThrownBy(() -> recipeService.cook(cookRequest("recipe:missing", 3)))
        .isInstanceOf(NotFoundException.class);
  }

  @Test
  void givenNonPositiveLimit_whenCooking_thenRequestIsRejected() {
    assertThatThrownBy(() -> recipeService.cook(cookRequest("recipe:soup", 0)))
        .isInstanceOf(InvalidRequestException.class);
  }

  private static CookRequestDto cookRequest(String recipeId, int limit) {
    CookRequestDto request = new CookRequestDto();
    request.identifiantRecette = recipeId;
    request.limiteParIngredient = limit;
    return request;
  }

  private static RecipeSearchRequestDto request(String type, String description, int limit) {
    RecipeSearchRequestDto request = new RecipeSearchRequestDto();
    request.typeRecette = type;
    request.description = description;
    request.limite = limit;
    return request;
  }
}
