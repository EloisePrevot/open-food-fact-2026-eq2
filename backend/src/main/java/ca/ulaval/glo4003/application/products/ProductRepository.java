package ca.ulaval.glo4003.application.products;

import ca.ulaval.glo4003.application.products.model.ProductDocument;
import ca.ulaval.glo4003.application.products.model.QualityIndicatorCounts;
import java.util.List;
import java.util.Map;

public interface ProductRepository {

  void saveAll(List<ProductDocument> products);

  List<ProductDocument> findByIds(List<String> ids);

  QualityIndicatorCounts countQualityIndicators();

  Map<String, Long> countByCategory();
}
