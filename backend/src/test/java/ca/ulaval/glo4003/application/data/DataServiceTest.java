package ca.ulaval.glo4003.application.data;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.QualityIndicatorCounts;
import ca.ulaval.glo4003.application.shared.NotFoundException;
import ca.ulaval.glo4003.ws.api.data.dto.ExtractedDataDto;
import ca.ulaval.glo4003.ws.api.data.dto.RawDataDto;
import ca.ulaval.glo4003.ws.api.data.dto.TransformedDataDto;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DataServiceTest {

  private static final String IDENTIFIANT = "off:000000000054";
  private static final String PAYLOAD = "{\"code\":\"000000000054\",\"brands\":\"\"}";
  private static final String INGESTED_AT = "2026-10-10T15:04:00+00:00";

  private RawRecordRepository rawRecordRepository;
  private RawDataRepository rawDataRepository;
  private ProductRepository productRepository;
  private DataService dataService;

  @BeforeEach
  void setUp() {
    rawRecordRepository = mock(RawRecordRepository.class);
    rawDataRepository = mock(RawDataRepository.class);
    productRepository = mock(ProductRepository.class);
    dataService = new DataService(rawRecordRepository, rawDataRepository, productRepository);
  }

  @Test
  void whenGettingExtractedData_thenEachSourceIsCounted() {
    when(rawRecordRepository.countBySource(DataSource.OPEN_FOOD_FACTS)).thenReturn(10L);
    when(rawRecordRepository.countBySource(DataSource.CANADIAN_NUTRIENT_FILE)).thenReturn(20L);
    when(rawRecordRepository.countBySource(DataSource.EXTENDED_RECIPES_DATASET)).thenReturn(30L);

    ExtractedDataDto extractedData = dataService.getExtractedData();

    assertThat(extractedData.nbProduitsAlimentairesScannes).isEqualTo(10);
    assertThat(extractedData.nbProduitsAlimentairesDeBase).isEqualTo(20);
    assertThat(extractedData.nbRecettesCuisine).isEqualTo(30);
  }

  @Test
  void whenGettingTransformedData_thenIndicatorsAndCategoriesAreReturned() {
    when(productRepository.countQualityIndicators())
        .thenReturn(new QualityIndicatorCounts(1, 2, 3));
    when(productRepository.countByCategory()).thenReturn(Map.of("Légumes", 4L));

    TransformedDataDto transformedData = dataService.getTransformedData();

    assertThat(transformedData.indicateursDeQualite)
        .containsExactly(
            Map.entry("NutriScore", 1L), Map.entry("Nova", 2L), Map.entry("EcoScore", 3L));
    assertThat(transformedData.categoriesProduitAlimentaire)
        .containsExactly(Map.entry("Légumes", 4L));
  }

  @Test
  void givenKnownIdentifiant_whenGettingRawData_thenOriginalPayloadIsReturned() {
    when(rawDataRepository.findByIdentifiant(IDENTIFIANT))
        .thenReturn(
            Optional.of(
                new RawRecord(IDENTIFIANT, DataSource.OPEN_FOOD_FACTS, INGESTED_AT, PAYLOAD)));

    RawDataDto rawData = dataService.getRawData(IDENTIFIANT);

    assertThat(rawData.identifiant).isEqualTo(IDENTIFIANT);
    assertThat(rawData.source).isEqualTo("open_food_facts");
    assertThat(rawData.dateIngestion).isEqualTo(INGESTED_AT);
    assertThat(rawData.chargeUtile).isEqualTo(PAYLOAD);
  }

  @Test
  void givenUnknownIdentifiant_whenGettingRawData_thenNotFoundIsThrown() {
    when(rawDataRepository.findByIdentifiant(IDENTIFIANT)).thenReturn(Optional.empty());

    assertThatThrownBy(() -> dataService.getRawData(IDENTIFIANT))
        .isInstanceOf(NotFoundException.class);
  }
}
