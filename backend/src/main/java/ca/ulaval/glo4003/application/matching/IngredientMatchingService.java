package ca.ulaval.glo4003.application.matching;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.search.IngredientSearchRepository;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import ca.ulaval.glo4003.application.search.model.ScoredProduct;
import ca.ulaval.glo4003.application.shared.InvalidRequestException;
import ca.ulaval.glo4003.application.shared.NotImplementedException;
import ca.ulaval.glo4003.ws.api.matching.dto.BrandSuggestionResponseDto;
import ca.ulaval.glo4003.ws.api.matching.dto.ContainsRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.ContainsResponseDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchRequestDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchResponseDto;
import ca.ulaval.glo4003.ws.api.matching.dto.IngredientMatchResponseDto.IngredientCandidateDto;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;

public class IngredientMatchingService {

  private static final int OVER_FETCH_FACTOR = 5;
  private static final int MIN_BRAND_QUERY_LENGTH = 2;
  private static final int DEFAULT_BRAND_SUGGESTIONS = 10;

  private final IngredientSearchRepository ingredientSearchRepository;
  private final ProductRepository productRepository;
  private final TextEmbedder textEmbedder;

  public IngredientMatchingService(
      IngredientSearchRepository ingredientSearchRepository,
      ProductRepository productRepository,
      TextEmbedder textEmbedder) {
    this.ingredientSearchRepository = ingredientSearchRepository;
    this.productRepository = productRepository;
    this.textEmbedder = textEmbedder;
  }

  public IngredientMatchResponseDto matchIngredient(IngredientMatchRequestDto request) {
    String ingredient = validate(request);
    ProductPreferences preferences =
        new ProductPreferences(request.marque, request.nutriScoreMin, request.novaMax);
    List<ScoredProductDocument> matches =
        recommendProducts(
            ingredient, preferences, Optional.ofNullable(request.produitDeBase), request.limite);

    IngredientMatchResponseDto response = new IngredientMatchResponseDto();
    response.ingredient = ingredient;
    response.candidats = matches.stream().map(IngredientMatchingService::toCandidate).toList();
    return response;
  }

  /**
   * Finds products similar to an ingredient, keeps only those satisfying the hard preferences, and
   * returns at most {@code limit} of them in similarity order. Over-fetches from the search index
   * so that filtering still yields results.
   */
  public List<ScoredProductDocument> recommendProducts(
      String ingredient,
      ProductPreferences preferences,
      Optional<Boolean> produitDeBase,
      int limit) {
    List<ScoredProduct> scoredProducts =
        ingredientSearchRepository.searchSimilar(
            textEmbedder.embed(ingredient), produitDeBase, limit * OVER_FETCH_FACTOR);
    Map<String, ProductDocument> products = findByIds(scoredProducts);
    return scoredProducts.stream()
        .filter(scored -> products.containsKey(scored.identifiant()))
        .map(
            scored -> new ScoredProductDocument(scored.score(), products.get(scored.identifiant())))
        .filter(scored -> preferences.accepts(scored.product()))
        .limit(limit)
        .toList();
  }

  public BrandSuggestionResponseDto suggestBrands(String query, int limit) {
    BrandSuggestionResponseDto response = new BrandSuggestionResponseDto();
    String normalized = Optional.ofNullable(query).map(String::strip).orElse("");
    int effectiveLimit = limit <= 0 ? DEFAULT_BRAND_SUGGESTIONS : limit;
    response.marques =
        normalized.length() < MIN_BRAND_QUERY_LENGTH
            ? List.of()
            : productRepository.findBrands(normalized, effectiveLimit);
    return response;
  }

  public ContainsResponseDto findProductsContainingIngredient(ContainsRequestDto request) {
    throw new NotImplementedException();
  }

  private Map<String, ProductDocument> findByIds(List<ScoredProduct> scoredProducts) {
    List<String> ids = scoredProducts.stream().map(ScoredProduct::identifiant).toList();
    return productRepository.findByIds(ids).stream()
        .collect(Collectors.toMap(ProductDocument::identifiant, Function.identity()));
  }

  private static IngredientCandidateDto toCandidate(ScoredProductDocument scored) {
    ProductDocument product = scored.product();
    IngredientCandidateDto candidate = new IngredientCandidateDto();
    candidate.identifiant = product.identifiant();
    candidate.nomProduit = product.nomProduit();
    candidate.score = scored.score();
    candidate.produitDeBase = product.produitDeBase();
    candidate.nutriScore = product.nutriScore();
    candidate.nova = product.nova();
    candidate.marques = product.marques();
    return candidate;
  }

  private static String validate(IngredientMatchRequestDto request) {
    if (request == null || request.limite <= 0) {
      throw new InvalidRequestException("La limite doit être un entier positif.");
    }
    String ingredient = Optional.ofNullable(request.ingredient).map(String::strip).orElse("");
    if (ingredient.isEmpty()) {
      throw new InvalidRequestException("L'ingrédient est obligatoire.");
    }
    return ingredient;
  }
}
