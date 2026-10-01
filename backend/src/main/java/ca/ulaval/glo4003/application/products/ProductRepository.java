package ca.ulaval.glo4003.application.products;

import ca.ulaval.glo4003.application.products.model.ProductDocument;
import java.util.List;

public interface ProductRepository {

  void saveAll(List<ProductDocument> products);

  List<ProductDocument> findByIds(List<String> ids);
}
