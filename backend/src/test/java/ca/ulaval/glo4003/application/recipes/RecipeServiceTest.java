package ca.ulaval.glo4003.application.recipes;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import ca.ulaval.glo4003.application.search.model.ScoredRecipe;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
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
  private TextEmbedder textEmbedder;
  private RecipeService recipeService;

  @BeforeEach
  void setUp() {
    recipeRepository = mock(RecipeRepository.class);
    recipeSearchRepository = mock(RecipeSearchRepository.class);
    textEmbedder = mock(TextEmbedder.class);
    recipeService = new RecipeService(recipeRepository, recipeSearchRepository, textEmbedder);
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
  void givenNonPositiveLimit_whenSearching_thenRequestIsRejected() {
    assertThatThrownBy(() -> recipeService.searchRecipes(request(null, null, 0)))
        .isInstanceOf(InvalidRequestException.class);
  }

  private static RecipeSearchRequestDto request(String type, String description, int limit) {
    RecipeSearchRequestDto request = new RecipeSearchRequestDto();
    request.typeRecette = type;
    request.description = description;
    request.limite = limit;
    return request;
  }
}
