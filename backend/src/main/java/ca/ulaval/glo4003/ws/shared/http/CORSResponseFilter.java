package ca.ulaval.glo4003.ws.shared.http;

import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.core.MultivaluedMap;
import java.io.IOException;

/**
 * Cette classe ajoute des en-têtes à la réponse afin de permettre à l'application d'envoyer des
 * requêtes HTTP vers un domaine différent de celui qui héberge le site.
 *
 * <p>Requêtes HTTP interorigines : <a
 * href="https://developer.mozilla.org/fr/docs/Web/HTTP/CORS">https://developer.mozilla.org/fr/docs/Web/HTTP/CORS</a>
 */
public class CORSResponseFilter implements ContainerResponseFilter {
  @Override
  public void filter(
      ContainerRequestContext requestContext, ContainerResponseContext responseContext)
      throws IOException {
    MultivaluedMap<String, Object> headers = responseContext.getHeaders();

    headers.add("Access-Control-Allow-Origin", "*");
    headers.add("Access-Control-Allow-Methods", "GET, POST, DELETE, PUT");
    headers.add("Access-Control-Allow-Headers", "X-Requested-With, Content-Type");
  }
}
