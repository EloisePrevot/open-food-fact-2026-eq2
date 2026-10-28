package ca.ulaval.glo4003;

import ca.ulaval.glo4003.application.data.DataService;
import ca.ulaval.glo4003.application.documentation.DocumentationService;
import ca.ulaval.glo4003.application.etl.EtlService;
import ca.ulaval.glo4003.application.matching.IngredientMatchingService;
import ca.ulaval.glo4003.application.recipes.RecipeService;
import ca.ulaval.glo4003.infrastructure.embedding.EmbeddingConfiguration;
import ca.ulaval.glo4003.infrastructure.embedding.OnnxTextEmbedder;
import ca.ulaval.glo4003.infrastructure.etl.EtlConfiguration;
import ca.ulaval.glo4003.infrastructure.etl.PythonEtlRunner;
import ca.ulaval.glo4003.persistence.PersistenceClients;
import ca.ulaval.glo4003.persistence.PersistenceConfiguration;
import ca.ulaval.glo4003.persistence.mongo.MongoProductRepository;
import ca.ulaval.glo4003.persistence.mongo.MongoRawReferenceRepository;
import ca.ulaval.glo4003.persistence.mongo.MongoRecipeRepository;
import ca.ulaval.glo4003.persistence.qdrant.QdrantRecipeSearchRepository;
import ca.ulaval.glo4003.persistence.sqlite.SqliteRawRecordRepository;
import ca.ulaval.glo4003.ws.api.data.DataResource;
import ca.ulaval.glo4003.ws.api.data.DataResourceImpl;
import ca.ulaval.glo4003.ws.api.documentation.DocumentationResource;
import ca.ulaval.glo4003.ws.api.documentation.DocumentationResourceImpl;
import ca.ulaval.glo4003.ws.api.heartbeat.HeartbeatResource;
import ca.ulaval.glo4003.ws.api.heartbeat.HeartbeatResourceImpl;
import ca.ulaval.glo4003.ws.api.matching.IngredientMatchingResource;
import ca.ulaval.glo4003.ws.api.matching.IngredientMatchingResourceImpl;
import ca.ulaval.glo4003.ws.api.recipe.RecipeResource;
import ca.ulaval.glo4003.ws.api.recipe.RecipeResourceImpl;
import ca.ulaval.glo4003.ws.shared.http.CORSResponseFilter;
import java.net.URI;
import java.util.concurrent.Executors;
import org.eclipse.jetty.server.Server;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.jetty.JettyHttpContainerFactory;
import org.glassfish.jersey.server.ResourceConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/** Configuration de l'API REST sans conteneur d'injection de dépendances ni Spring. */
@SuppressWarnings("all")
public class ProjectDBMain {
  private static final Logger LOGGER = LoggerFactory.getLogger(ProjectDBMain.class);

  public static boolean isDev =
      true; // Serait normalement un argument JVM ou une valeur dans un fichier .properties.
  public static final String BASE_URI = "http://localhost:8080/";

  public static void main(String[] args) throws Exception {

    LOGGER.info("Setup persistence clients");
    PersistenceClients persistenceClients =
        PersistenceClients.connect(PersistenceConfiguration.fromEnvironment());

    LOGGER.info("Setup resources (API)");
    HeartbeatResource heartbeatResource = createHeartbeatResource();
    DataResource dataResource = createDataResource(persistenceClients);
    DocumentationResource documentationResource = createDocumentationResource();
    RecipeResource recipeResource = createRecipeResource(persistenceClients);
    IngredientMatchingResource ingredientMatchingResource = createIngredientMatchingResource();

    final AbstractBinder binder =
        new AbstractBinder() {
          @Override
          protected void configure() {
            bind(heartbeatResource).to(HeartbeatResource.class);
            bind(dataResource).to(DataResource.class);
            bind(documentationResource).to(DocumentationResource.class);
            bind(recipeResource).to(RecipeResource.class);
            bind(ingredientMatchingResource).to(IngredientMatchingResource.class);
          }
        };

    final ResourceConfig config = new ResourceConfig();
    config.register(binder);
    config.register(new CORSResponseFilter());
    config.packages("ca.ulaval.glo4003.ws.api");

    try {
      LOGGER.info("Setup http server");
      final Server server = JettyHttpContainerFactory.createServer(URI.create(BASE_URI), config);

      Runtime.getRuntime()
          .addShutdownHook(
              new Thread(
                  () -> {
                    try {
                      LOGGER.info("Shutting down the application...");
                      server.stop();
                      persistenceClients.close();
                      LOGGER.info("Done, exit.");
                    } catch (Exception e) {
                      LOGGER.error("Error shutting down the server", e);
                    }
                  }));

      LOGGER.info("Application started.%nStop the application using CTRL+C");
      startEtlIfEnabled();

      // Bloquer le thread et attendre un signal d'arrêt, comme CTRL+C.
      Thread.currentThread().join();

    } catch (InterruptedException e) {
      LOGGER.error("Error startig up the server", e);
    }
  }

  private static HeartbeatResource createHeartbeatResource() {
    LOGGER.info("Setup heartbeat resource");
    return new HeartbeatResourceImpl();
  }

  private static DataResource createDataResource(PersistenceClients persistenceClients) {
    LOGGER.info("Setup data resource");
    return new DataResourceImpl(
        new DataService(
            new SqliteRawRecordRepository(persistenceClients),
            new MongoRawReferenceRepository(persistenceClients),
            new MongoProductRepository(persistenceClients)));
  }

  private static DocumentationResource createDocumentationResource() {
    LOGGER.info("Setup documentation resource");
    return new DocumentationResourceImpl(new DocumentationService());
  }

  private static RecipeResource createRecipeResource(PersistenceClients persistenceClients) {
    LOGGER.info("Setup recipe resource");
    return new RecipeResourceImpl(
        new RecipeService(
            new MongoRecipeRepository(persistenceClients),
            new QdrantRecipeSearchRepository(persistenceClients),
            new OnnxTextEmbedder(EmbeddingConfiguration.fromEnvironment().modelDirectory())));
  }

  private static IngredientMatchingResource createIngredientMatchingResource() {
    LOGGER.info("Setup ingredient matching resource");
    return new IngredientMatchingResourceImpl(new IngredientMatchingService());
  }

  private static void startEtlIfEnabled() {
    EtlConfiguration configuration = EtlConfiguration.fromEnvironment();
    if (!configuration.runAtStartup()) {
      LOGGER.info("ETL au démarrage désactivé (ELT_AU_DEMARRAGE=false)");
      return;
    }
    createEtlService(configuration).startInBackground();
  }

  private static EtlService createEtlService(EtlConfiguration configuration) {
    return new EtlService(
        new PythonEtlRunner(configuration.pythonCommand(), configuration.eltDirectory()),
        Executors.newSingleThreadExecutor(
            Thread.ofPlatform().name("etl-arriere-plan").daemon().factory()),
        configuration.limit());
  }
}
