package ca.ulaval.glo4003.application.matching;

import ca.ulaval.glo4003.application.products.model.ProductDocument;

public record ScoredProductDocument(double score, ProductDocument product) {}
