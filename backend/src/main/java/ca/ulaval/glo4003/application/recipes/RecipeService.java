package ca.ulaval.glo4003.application.recipes;

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
import ca.ulaval.glo4003.ws.api.recipe.dto.CookResponseDto.IngredientRecommendationDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.CookResponseDto.RecommendedProductDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeDetailDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeDetailDto.RecipeIngredientDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchRequestDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchResponseDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeSearchResponseDto.RecipeSummaryDto;
import ca.ulaval.glo4003.ws.api.recipe.dto.RecipeTypesDto;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

public class RecipeService {

  private final RecipeRepository recipeRepository;
  private final RecipeSearchRepository recipeSearchRepository;
  private final IngredientMatchingService ingredientMatchingService;
  private final TextEmbedder textEmbedder;

  public RecipeService(
      RecipeRepository recipeRepository,
      RecipeSearchRepository recipeSearchRepository,
      IngredientMatchingService ingredientMatchingService,
      TextEmbedder textEmbedder) {
    this.recipeRepository = recipeRepository;
    this.recipeSearchRepository = recipeSearchRepository;
    this.ingredientMatchingService = ingredientMatchingService;
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

  public RecipeDetailDto getRecipe(String identifiant) {
    return recipeRepository
        .findDetailById(identifiant)
        .map(RecipeService::toDetail)
        .orElseThrow(
            () -> new NotFoundException("Aucune recette pour l'identifiant " + identifiant));
  }

  public CookResponseDto cook(CookRequestDto request) {
    validateCook(request);
    ProductPreferences preferences =
        new ProductPreferences(request.marque, request.nutriScoreMin, request.novaMax);
    RecipeDetailDocument recipe =
        recipeRepository
            .findDetailById(request.identifiantRecette)
            .orElseThrow(
                () ->
                    new NotFoundException(
                        "Aucune recette pour l'identifiant " + request.identifiantRecette));

    Optional<Boolean> produitDeBase = Optional.ofNullable(request.preferenceProduitDeBase);

    CookResponseDto response = new CookResponseDto();
    response.identifiantRecette = recipe.identifiant();
    response.nomRecette = recipe.nom();
    response.ingredients = new ArrayList<>();
    response.ingredientsSansCorrespondance = new ArrayList<>();

    for (RecipeIngredient ingredient : recipe.ingredients()) {
      List<ScoredProductDocument> matches =
          ingredientMatchingService.recommendProducts(
              ingredient.nom(), preferences, produitDeBase, request.limiteParIngredient);
      if (matches.isEmpty()) {
        response.ingredientsSansCorrespondance.add(ingredient.texteOriginal());
      } else {
        response.ingredients.add(toRecommendation(ingredient, matches));
      }
    }
    return response;
  }

  private static IngredientRecommendationDto toRecommendation(
      RecipeIngredient ingredient, List<ScoredProductDocument> matches) {
    IngredientRecommendationDto recommendation = new IngredientRecommendationDto();
    recommendation.ingredientTexte = ingredient.texteOriginal();
    recommendation.produits = matches.stream().map(RecipeService::toRecommendedProduct).toList();
    return recommendation;
  }

  private static RecommendedProductDto toRecommendedProduct(ScoredProductDocument scored) {
    ProductDocument product = scored.product();
    RecommendedProductDto dto = new RecommendedProductDto();
    dto.identifiant = product.identifiant();
    dto.nomProduit = product.nomProduit();
    dto.marque = product.marques().isEmpty() ? null : product.marques().get(0);
    dto.nutriScore = product.nutriScore();
    dto.nova = product.nova();
    dto.produitDeBase = product.produitDeBase();
    dto.score = scored.score();
    return dto;
  }

  private static void validateCook(CookRequestDto request) {
    if (request == null || request.limiteParIngredient <= 0) {
      throw new InvalidRequestException("La limite par ingrédient doit être un entier positif.");
    }
    if (nonBlank(request.identifiantRecette).isEmpty()) {
      throw new InvalidRequestException("L'identifiant de la recette est obligatoire.");
    }
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

  private static RecipeDetailDto toDetail(RecipeDetailDocument recipe) {
    RecipeDetailDto detail = new RecipeDetailDto();
    detail.identifiant = recipe.identifiant();
    detail.nom = recipe.nom();
    detail.description = recipe.description();
    detail.type = recipe.types();
    detail.etapes = recipe.etapes();
    detail.ingredients = recipe.ingredients().stream().map(RecipeService::toIngredient).toList();
    return detail;
  }

  private static RecipeIngredientDto toIngredient(
      RecipeDetailDocument.RecipeIngredient ingredient) {
    RecipeIngredientDto dto = new RecipeIngredientDto();
    dto.nom = ingredient.nom();
    dto.cle = ingredient.cle();
    dto.texteOriginal = ingredient.texteOriginal();
    return dto;
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
