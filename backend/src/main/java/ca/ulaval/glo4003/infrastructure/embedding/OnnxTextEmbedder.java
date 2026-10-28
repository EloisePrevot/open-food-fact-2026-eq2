package ca.ulaval.glo4003.infrastructure.embedding;

import ai.djl.huggingface.tokenizers.Encoding;
import ai.djl.huggingface.tokenizers.HuggingFaceTokenizer;
import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtException;
import ai.onnxruntime.OrtSession;
import ca.ulaval.glo4003.application.search.TextEmbedder;
import com.google.common.base.Suppliers;
import java.io.IOException;
import java.nio.LongBuffer;
import java.nio.file.Path;
import java.util.Map;
import java.util.function.Supplier;

public class OnnxTextEmbedder implements TextEmbedder {

  private static final Map<String, String> TOKENIZER_OPTIONS =
      Map.of("truncation", "true", "maxLength", "128", "padding", "false");

  private final Supplier<LoadedModel> model;

  public OnnxTextEmbedder(Path modelDirectory) {
    model = Suppliers.memoize(() -> LoadedModel.load(ModelFiles.locate(modelDirectory)));
  }

  @Override
  public float[] embed(String text) {
    LoadedModel loadedModel = model.get();
    Encoding encoding = loadedModel.tokenizer().encode(text);
    try (OnnxTensor ids = loadedModel.tensor(encoding.getIds());
        OnnxTensor attentionMask = loadedModel.tensor(encoding.getAttentionMask());
        OnnxTensor typeIds = loadedModel.tensor(encoding.getTypeIds());
        OrtSession.Result result =
            loadedModel
                .session()
                .run(
                    Map.of(
                        "input_ids", ids,
                        "attention_mask", attentionMask,
                        "token_type_ids", typeIds))) {
      float[][] tokenEmbeddings = ((float[][][]) result.get(0).getValue())[0];
      return meanPooling(tokenEmbeddings, encoding.getAttentionMask());
    } catch (OrtException exception) {
      throw new EmbeddingException("Vectorisation impossible", exception);
    }
  }

  static float[] meanPooling(float[][] tokenEmbeddings, long[] attentionMask) {
    float[] pooled = new float[tokenEmbeddings[0].length];
    long tokenCount = 0;
    for (int token = 0; token < tokenEmbeddings.length; token++) {
      if (attentionMask[token] == 0) {
        continue;
      }
      tokenCount++;
      for (int dimension = 0; dimension < pooled.length; dimension++) {
        pooled[dimension] += tokenEmbeddings[token][dimension];
      }
    }
    for (int dimension = 0; dimension < pooled.length; dimension++) {
      pooled[dimension] /= Math.max(tokenCount, 1);
    }
    return pooled;
  }

  private record LoadedModel(
      HuggingFaceTokenizer tokenizer, OrtEnvironment environment, OrtSession session) {

    static LoadedModel load(ModelFiles files) {
      OrtEnvironment environment = OrtEnvironment.getEnvironment();
      try {
        return new LoadedModel(
            HuggingFaceTokenizer.newInstance(files.tokenizer(), TOKENIZER_OPTIONS),
            environment,
            environment.createSession(files.model().toString(), new OrtSession.SessionOptions()));
      } catch (IOException | OrtException exception) {
        throw new EmbeddingException(
            "Chargement du modèle " + files.model() + " impossible", exception);
      }
    }

    OnnxTensor tensor(long[] values) throws OrtException {
      return OnnxTensor.createTensor(
          environment, LongBuffer.wrap(values), new long[] {1, values.length});
    }
  }
}
