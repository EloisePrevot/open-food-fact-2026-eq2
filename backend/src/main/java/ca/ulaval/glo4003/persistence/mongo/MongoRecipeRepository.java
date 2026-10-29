package ca.ulaval.glo4003.persistence.mongo;

import static com.mongodb.client.model.Filters.empty;
import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Filters.in;
import static com.mongodb.client.model.Projections.include;
import static com.mongodb.client.model.Sorts.ascending;

import ca.ulaval.glo4003.application.recipes.RecipeRepository;
import ca.ulaval.glo4003.application.recipes.model.RecipeDetailDocument;
import ca.ulaval.glo4003.application.recipes.model.RecipeDetailDocument.RecipeIngredient;
import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.bson.Document;
import org.bson.conversions.Bson;

public class MongoRecipeRepository implements RecipeRepository {

  private static final String NAME_FIELD = "nom";
  private static final String TYPE_FIELD = "type";
  private static final String INGREDIENT_COUNT_FIELD = "nbIngredients";
  private static final String DESCRIPTION_FIELD = "description";
  private static final String INGREDIENTS_FIELD = "ingredients";
  private static final String STEPS_FIELD = "etapes";
  private static final String INGREDIENT_NAME_FIELD = "nom";
  private static final String INGREDIENT_KEY_FIELD = "cle";
  private static final String INGREDIENT_ORIGINAL_FIELD = "texteOriginal";
  private static final String CORPUS_ORDER_FIELD = "refBrut.ordinal";
  private static final Bson SUMMARY_FIELDS =
      include(NAME_FIELD, TYPE_FIELD, INGREDIENT_COUNT_FIELD);
  private static final Bson DETAIL_FIELDS =
      include(NAME_FIELD, TYPE_FIELD, DESCRIPTION_FIELD, INGREDIENTS_FIELD, STEPS_FIELD);

  private final MongoCollection<Document> recipes;

  public MongoRecipeRepository(PersistenceClients persistenceClients) {
    recipes = persistenceClients.mongoDatabase().getCollection(MongoCollections.RECIPES);
  }

  @Override
  public void saveAll(List<RecipeDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public Optional<RecipeDocument> findById(String id) {
    return Optional.ofNullable(summaries(eq("_id", id)).first())
        .map(MongoRecipeRepository::toRecipe);
  }

  @Override
  public Optional<RecipeDetailDocument> findDetailById(String id) {
    return Optional.ofNullable(recipes.find(eq("_id", id)).projection(DETAIL_FIELDS).first())
        .map(MongoRecipeRepository::toRecipeDetail);
  }

  @Override
  public List<RecipeDocument> findByIds(List<String> ids) {
    return toRecipes(summaries(in("_id", ids)));
  }

  @Override
  public List<RecipeDocument> findFirst(Optional<String> recipeType, int limit) {
    Bson filter = recipeType.map(type -> eq(TYPE_FIELD, type)).orElse(empty());
    return toRecipes(summaries(filter).sort(ascending(CORPUS_ORDER_FIELD)).limit(limit));
  }

  @Override
  public List<String> findTypes() {
    return recipes.distinct(TYPE_FIELD, String.class).into(new ArrayList<>()).stream()
        .sorted()
        .toList();
  }

  private FindIterable<Document> summaries(Bson filter) {
    return recipes.find(filter).projection(SUMMARY_FIELDS);
  }

  private static List<RecipeDocument> toRecipes(FindIterable<Document> documents) {
    return documents.map(MongoRecipeRepository::toRecipe).into(new ArrayList<>());
  }

  private static RecipeDocument toRecipe(Document document) {
    return new RecipeDocument(
        document.getString("_id"),
        document.getString(NAME_FIELD),
        document.getList(TYPE_FIELD, String.class, List.of()),
        document.get(INGREDIENT_COUNT_FIELD, Number.class).intValue());
  }

  private static RecipeDetailDocument toRecipeDetail(Document document) {
    return new RecipeDetailDocument(
        document.getString("_id"),
        document.getString(NAME_FIELD),
        document.getString(DESCRIPTION_FIELD),
        document.getList(TYPE_FIELD, String.class, List.of()),
        toIngredients(document),
        document.getList(STEPS_FIELD, String.class, List.of()));
  }

  private static List<RecipeIngredient> toIngredients(Document document) {
    return document.getList(INGREDIENTS_FIELD, Document.class, List.of()).stream()
        .map(
            ingredient ->
                new RecipeIngredient(
                    ingredient.getString(INGREDIENT_NAME_FIELD),
                    ingredient.getString(INGREDIENT_KEY_FIELD),
                    ingredient.getString(INGREDIENT_ORIGINAL_FIELD)))
        .toList();
  }
}
