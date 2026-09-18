package ca.ulaval.glo4003;

import ca.ulaval.glo4003.ws.api.heartbeat.HeartbeatResource;
import ca.ulaval.glo4003.ws.api.heartbeat.HeartbeatResourceImpl;
import ca.ulaval.glo4003.ws.shared.http.CORSResponseFilter;
import java.net.URI;
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

    LOGGER.info("Setup resources (API)");
    HeartbeatResource heartbeatResource = createHeartbeatResource();

    final AbstractBinder binder =
        new AbstractBinder() {
          @Override
          protected void configure() {
            bind(heartbeatResource).to(HeartbeatResource.class);
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
                      LOGGER.info("Done, exit.");
                    } catch (Exception e) {
                      LOGGER.error("Error shutting down the server", e);
                    }
                  }));

      LOGGER.info("Application started.%nStop the application using CTRL+C");

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
}
