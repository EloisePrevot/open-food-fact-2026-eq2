package ca.ulaval.glo4003.application.data.model;

public record RawRecord(
    String identifiant, DataSource source, String ingestedAt, String payloadJson) {}
