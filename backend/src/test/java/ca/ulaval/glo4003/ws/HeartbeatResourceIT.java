package ca.ulaval.glo4003.ws;

import static io.restassured.RestAssured.given;
import static org.awaitility.Awaitility.await;
import static org.hamcrest.Matchers.notNullValue;

import ca.ulaval.glo4003.ProjectDBMain;
import io.restassured.RestAssured;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import java.time.Duration;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

public class HeartbeatResourceIT {
  private static final String HEARTBEAT_PATH = "/heartbeat";
  private static final Duration STARTUP_TIMEOUT = Duration.ofSeconds(30);
  private static final Duration POLL_INTERVAL = Duration.ofMillis(200);

  private static Thread t;

  @BeforeAll
  public static void setUp() {
    RestAssured.filters(new RequestLoggingFilter(), new ResponseLoggingFilter());

    t =
        new Thread(
            () -> {
              try {
                ProjectDBMain.main(new String[] {});
              } catch (Exception e) {
                e.printStackTrace();
              }
            });
    t.setDaemon(true);
    t.start();

    waitUntilServerIsReady();
  }

  private static void waitUntilServerIsReady() {
    await()
        .atMost(STARTUP_TIMEOUT)
        .pollInterval(POLL_INTERVAL)
        .ignoreExceptions()
        .untilAsserted(() -> given().get(HEARTBEAT_PATH).then().statusCode(200));
  }

  @AfterAll
  public static void tearDown() {
    t.interrupt();
  }

  @Test
  public void whenGetHeartbeat_thenApplicationNameReturned() {
    given().get(HEARTBEAT_PATH).then().body("nomApplication", notNullValue());
  }
}
