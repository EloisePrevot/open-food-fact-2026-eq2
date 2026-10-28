package ca.ulaval.glo4003.application.recipes;

import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import ca.ulaval.glo4003.application.search.RecipeSearchRepository;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import ca.ulaval.glo4003.application.search.model.ScoredRecipe;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import ca.ulaval.glo4003.application.shared.NotImplementedException;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookResponseDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchResponseDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchResponseDto.RecipeSummaryDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeTypesDto;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

public class RecipeService {

  private final RecipeRepository recipeRepository;
  private final RecipeSearchRepository recipeSearchRepository;
  private final TextEmbedder textEmbedder;

  public RecipeService(
      RecipeRepository recipeRepository,
      RecipeSearchRepository recipeSearchRepository,
      TextEmbedder textEmbedder) {
    this.recipeRepository = recipeRepository;
    this.recipeSearchRepository = recipeSearchRepository;
    this.textEmbedder = textEmbedder;
  }

  public RecipeTypesDto getRecipeTypes() {
    RecipeTypesDto recipeTypes = new RecipeTypesDto();
    recipeTypes.typesRecette = recipeRepository.findTypes();
    return recipeTypes;
  }

  public RecipeSearchResponseDto searchRecipes(RecipeSearchRequestDto request) {
    validate(request);
    Optional<String> recipeType = nonBlank(request.typeRecette);
    RecipeSearchResponseDto response = new RecipeSearchResponseDto();
    response.recettes =
        nonBlank(request.description)
            .map(description -> rank(description, recipeType, request.limite))
            .orElseGet(() -> browse(recipeType, request.limite));
    return response;
  }

  public CookResponseDto cook(CookRequestDto request) {
    throw new NotImplementedException();
  }

  private List<RecipeSummaryDto> browse(Optional<String> recipeType, int limit) {
    return recipeRepository.findFirst(recipeType, limit).stream()
        .map(recipe -> toSummary(recipe, null))
        .toList();
  }

  private List<RecipeSummaryDto> rank(String description, Optional<String> recipeType, int limit) {
    List<ScoredRecipe> scoredRecipes =
        recipeSearchRepository.searchSimilar(textEmbedder.embed(description), recipeType, limit);
    Map<String, RecipeDocument> recipes = findByIds(scoredRecipes);
    return scoredRecipes.stream()
        .filter(scored -> recipes.containsKey(scored.identifiant()))
        .map(scored -> toSummary(recipes.get(scored.identifiant()), scored.score()))
        .toList();
  }

  private Map<String, RecipeDocument> findByIds(List<ScoredRecipe> scoredRecipes) {
    List<String> ids = scoredRecipes.stream().map(ScoredRecipe::identifiant).toList();
    return recipeRepository.findByIds(ids).stream()
        .collect(Collectors.toMap(RecipeDocument::identifiant, Function.identity()));
  }

  private static RecipeSummaryDto toSummary(RecipeDocument recipe, Double score) {
    RecipeSummaryDto summary = new RecipeSummaryDto();
    summary.identifiant = recipe.identifiant();
    summary.nom = recipe.nom();
    summary.type = recipe.types();
    summary.nbIngredients = recipe.nbIngredients();
    summary.score = score;
    return summary;
  }

  private static void validate(RecipeSearchRequestDto request) {
    if (request == null || request.limite <= 0) {
      throw new InvalidRequestException("La limite doit être un entier positif.");
    }
  }

  private static Optional<String> nonBlank(String value) {
    return Optional.ofNullable(value).map(String::strip).filter(text -> !text.isEmpty());
  }
}
