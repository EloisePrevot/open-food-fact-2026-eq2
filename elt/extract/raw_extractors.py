"""Extracteurs streaming des formats bruts pris en charge."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from collections.abc import Iterator

import ijson

from raw_models import RawArtifact, RawRecord


class RawRecordExtractor(ABC):
    """Strategy pour extraire des enregistrements sans les transformer."""

    @abstractmethod
    def extract(self, artifact: RawArtifact) -> Iterator[RawRecord]:
        """Retourne les enregistrements source dans leur ordre original."""


class CsvRecordExtractor(RawRecordExtractor):
    """Lit un CSV avec le module standard, y compris les champs multi-lignes."""

    delimiter = ","
    quoting = csv.QUOTE_MINIMAL

    def extract(self, artifact: RawArtifact) -> Iterator[RawRecord]:
        with artifact.path.open("r", encoding=artifact.encoding, newline="") as source_file:
            reader = csv.reader(source_file, delimiter=self.delimiter, quoting=self.quoting)
            raw_headers = next(reader, None)

            if raw_headers is None:
                return

            headers = self._normalize_headers(raw_headers)
            for ordinal, values in enumerate(reader, start=1):
                if not any(values):
                    continue
                if len(values) != len(headers):
                    raise ValueError(
                        f"Invalid record width in {artifact.relative_path} at record {ordinal}."
                    )

                yield RawRecord(ordinal=ordinal, payload=dict(zip(headers, values, strict=True)))

    @staticmethod
    def _normalize_headers(raw_headers: list[str]) -> list[str]:
        occurrences: dict[str, int] = {}
        headers: list[str] = []

        for index, header in enumerate(raw_headers):
            base_name = header or f"_unnamed_{index}"
            occurrence = occurrences.get(base_name, 0)
            occurrences[base_name] = occurrence + 1
            headers.append(base_name if occurrence == 0 else f"{base_name}_{occurrence}")

        return headers


class TsvRecordExtractor(CsvRecordExtractor):
    """Lit l'export Open Food Facts : séparateur tabulation, aucun guillemet de protection.

    QUOTE_NONE : OFF ne protège pas ses champs, un guillemet en début de champ
    est une donnée et ne doit pas avaler les lignes suivantes.
    """

    delimiter = "\t"
    quoting = csv.QUOTE_NONE

    def extract(self, artifact: RawArtifact) -> Iterator[RawRecord]:
        csv.field_size_limit(10_000_000)
        yield from super().extract(artifact)


class JsonArrayRecordExtractor(RawRecordExtractor):
    """Lit en flux les objets d’un tableau JSON racine."""

    def extract(self, artifact: RawArtifact) -> Iterator[RawRecord]:
        with artifact.path.open("rb") as source_file:
            for ordinal, payload in enumerate(ijson.items(source_file, "item"), start=1):
                if not isinstance(payload, dict):
                    raise ValueError(
                        f"Expected a JSON object in {artifact.relative_path} at record {ordinal}."
                    )

                yield RawRecord(ordinal=ordinal, payload=payload)


def extractor_for(artifact: RawArtifact) -> RawRecordExtractor:
    """Choisit l’extracteur selon le type de média de l’artefact."""
    extractors: dict[str, RawRecordExtractor] = {
        "text/csv": CsvRecordExtractor(),
        "text/tab-separated-values": TsvRecordExtractor(),
        "application/json": JsonArrayRecordExtractor(),
    }

    try:
        return extractors[artifact.media_type]
    except KeyError as error:
        raise ValueError(f"Unsupported media type: {artifact.media_type}") from error