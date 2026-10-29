package ca.ulaval.glo4003.application.products.model;

import java.util.List;

public record ProductDocument(
    String identifiant,
    String nomProduit,
    boolean produitDeBase,
    String nutriScore,
    Integer nova,
    List<String> marques) {}
