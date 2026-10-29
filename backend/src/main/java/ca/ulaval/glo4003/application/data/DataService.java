package ca.ulaval.glo4003.application.data;

import ca.ulaval.glo4003.application.data.model.DataSource;
import ca.ulaval.glo4003.application.data.model.RawRecord;
import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.QualityIndicatorCounts;
import ca.ulaval.glo4003.application.shared.NotFoundException;
import ca.ulaval.glo4003.ws.api.data.dto.ExtractedDataDto;
import ca.ulaval.glo4003.ws.api.data.dto.RawDataDto;
import ca.ulaval.glo4003.ws.api.data.dto.TransformedDataDto;
import java.util.LinkedHashMap;
import java.util.Map;

public class DataService {

  private final RawRecordRepository rawRecordRepository;
  private final RawDataRepository rawDataRepository;
  private final ProductRepository productRepository;

  public DataService(
      RawRecordRepository rawRecordRepository,
      RawDataRepository rawDataRepository,
      ProductRepository productRepository) {
    this.rawRecordRepository = rawRecordRepository;
    this.rawDataRepository = rawDataRepository;
    this.productRepository = productRepository;
  }

  public ExtractedDataDto getExtractedData() {
    ExtractedDataDto extractedData = new ExtractedDataDto();
    extractedData.nbProduitsAlimentairesScannes =
        rawRecordRepository.countBySource(DataSource.OPEN_FOOD_FACTS);
    extractedData.nbProduitsAlimentairesDeBase =
        rawRecordRepository.countBySource(DataSource.CANADIAN_NUTRIENT_FILE);
    extractedData.nbRecettesCuisine =
        rawRecordRepository.countBySource(DataSource.EXTENDED_RECIPES_DATASET);
    return extractedData;
  }

  public TransformedDataDto getTransformedData() {
    TransformedDataDto transformedData = new TransformedDataDto();
    transformedData.indicateursDeQualite =
        toQualityIndicators(productRepository.countQualityIndicators());
    transformedData.categoriesProduitAlimentaire = productRepository.countByCategory();
    return transformedData;
  }

  public RawDataDto getRawData(String identifiant) {
    RawRecord rawRecord =
        rawDataRepository.findByIdentifiant(identifiant).orElseThrow(() -> notFound(identifiant));
    return toRawDataDto(rawRecord);
  }

  private static Map<String, Long> toQualityIndicators(QualityIndicatorCounts counts) {
    Map<String, Long> indicators = new LinkedHashMap<>();
    indicators.put("NutriScore", counts.nutriScore());
    indicators.put("Nova", counts.nova());
    indicators.put("EcoScore", counts.ecoScore());
    return indicators;
  }

  private static RawDataDto toRawDataDto(RawRecord rawRecord) {
    RawDataDto rawData = new RawDataDto();
    rawData.identifiant = rawRecord.identifiant();
    rawData.source = rawRecord.source().rawName();
    rawData.dateIngestion = rawRecord.ingestedAt();
    rawData.chargeUtile = rawRecord.payloadJson();
    return rawData;
  }

  private static NotFoundException notFound(String identifiant) {
    return new NotFoundException("Aucun enregistrement pour l'identifiant " + identifiant);
  }
}
