package ca.ulaval.glo4003.application.etl;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;

import java.util.concurrent.Executor;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;

class EtlServiceTest {

  private static final int LIMIT = 0;
  private static final Executor SAME_THREAD = Runnable::run;

  private EtlRunner runner;

  @BeforeEach
  void setUp() {
    runner = mock(EtlRunner.class);
  }

  @Test
  void whenStartingInBackground_thenStepsRunInOrder() {
    new EtlService(runner, SAME_THREAD, LIMIT).startInBackground();

    InOrder order = inOrder(runner);
    order.verify(runner).run(EtlStep.EXTRACT.arguments(LIMIT));
    order.verify(runner).run(EtlStep.TRANSFORM.arguments(LIMIT));
    order.verify(runner).run(EtlStep.LOAD.arguments(LIMIT));
  }

  @Test
  void givenFailingStep_whenStartingInBackground_thenFollowingStepsAreSkipped() {
    doThrow(new EtlException("échec")).when(runner).run(EtlStep.EXTRACT.arguments(LIMIT));

    new EtlService(runner, SAME_THREAD, LIMIT).startInBackground();

    verify(runner).run(any());
  }

  @Test
  void whenStartingInBackground_thenPipelineIsDelegatedToExecutor() {
    Executor executor = mock(Executor.class);

    new EtlService(runner, executor, LIMIT).startInBackground();

    verify(executor).execute(any());
    verifyNoInteractions(runner);
  }
}
