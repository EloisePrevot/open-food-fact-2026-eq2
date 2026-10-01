"""Extraction des sources brutes vers des enregistrements non transformés."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path

from elt.config import Settings
from elt.connections import DatabaseConnections
from elt.raw_models import RawArtifact

CNF_SOURCE = "canadian_nutrient_file"
KAGGLE_SOURCE = "extended_recipes_dataset"
SUPPORTED_SOURCES = ("cnf", "kaggle")

_CNF_UTF8_FILENAMES = {
    "CONVERSION FACTOR.csv",
    "NUTRIENT AMOUNT.csv",
    "REFUSE AMOUNT.csv",
    "YIELD AMOUNT.csv",
}


def open_extraction_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs disponibles au futur extracteur, sans extraire de données."""
    return DatabaseConnections.connect(settings or Settings.from_environment())


def get_raw_artifacts(
    source_names: Sequence[str], settings: Settings | None = None
) -> Iterator[RawArtifact]:
    """Retourne uniquement les artefacts CNF et Kaggle autorisés à l’ingestion."""
    configured_settings = settings or Settings.from_environment()

    for source_name in source_names:
        if source_name == "cnf":
            yield from _get_cnf_artifacts(configured_settings.raw_directory)
        elif source_name == "kaggle":
            yield _get_kaggle_artifact(configured_settings.raw_directory)
        else:
            raise ValueError(f"Unsupported source: {source_name}")


def _get_cnf_artifacts(raw_directory: Path) -> Iterator[RawArtifact]:
    cnf_directory = raw_directory / "cnf-fcen-csv"

    for path in sorted(cnf_directory.glob("*.csv")):
        yield RawArtifact(
            source=CNF_SOURCE,
            path=path,
            relative_path=str(path.relative_to(raw_directory)),
            encoding="utf-8" if path.name in _CNF_UTF8_FILENAMES else "cp1252",
            media_type="text/csv",
        )


def _get_kaggle_artifact(raw_directory: Path) -> RawArtifact:
    path = raw_directory / "kaggle-recipes" / "recipes_extended.json"

    return RawArtifact(
        source=KAGGLE_SOURCE,
        path=path,
        relative_path=str(path.relative_to(raw_directory)),
        encoding="utf-8",
        media_type="application/json",
    )
