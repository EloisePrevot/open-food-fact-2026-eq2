package ca.ulaval.glo4003.persistence.mongo;

import ca.ulaval.glo4003.application.products.ProductRepository;
import ca.ulaval.glo4003.application.products.model.ProductDocument;
import java.util.List;

public class MongoProductRepository implements ProductRepository {

  @Override
  public void saveAll(List<ProductDocument> products) {
    throw new UnsupportedOperationException("Not implemented");
  }

  @Override
  public List<ProductDocument> findByIds(List<String> ids) {
    throw new UnsupportedOperationException("Not implemented");
  }
}
