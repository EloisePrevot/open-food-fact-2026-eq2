package ca.ulaval.glo4003.persistence.mongo;

import ca.ulaval.glo4003.application.recipes.RecipeRepository;
import ca.ulaval.glo4003.application.recipes.model.RecipeDocument;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import com.mongodb.client.MongoCollection;
import java.util.List;
import java.util.Optional;
import org.bson.Document;

public class MongoRecipeRepository implements RecipeRepository {
  private static final String COLLECTION_NAME = "recettes";

  private final MongoCollection<Document> recipes;

  public MongoRecipeRepository(PersistenceClients persistenceClients) {
    recipes = persistenceClients.mongoDatabase().getCollection(COLLECTION_NAME);
  }

  @Override
  public void saveAll(List<RecipeDocument> recipes) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public Optional<RecipeDocument> findById(String id) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<RecipeDocument> findByIds(List<String> ids) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<String> findTypes() {
    throw new UnsupportedOperationException("Not implemented");
  }
}
