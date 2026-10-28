"""Extraction des sources brutes vers des enregistrements non transformés."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path

from config import Settings
from raw_models import RawArtifact

CNF_SOURCE = "canadian_nutrient_file"
KAGGLE_SOURCE = "extended_recipes_dataset"
OFF_SOURCE = "open_food_facts"
SUPPORTED_SOURCES = ("cnf", "kaggle", "off")

_CNF_UTF8_FILENAMES = {
    "CONVERSION FACTOR.csv",
    "NUTRIENT AMOUNT.csv",
    "REFUSE AMOUNT.csv",
    "YIELD AMOUNT.csv",
}


def get_raw_artifacts(
    source_names: Sequence[str], settings: Settings | None = None
) -> Iterator[RawArtifact]:
    """Retourne uniquement les artefacts CNF, Kaggle et OFF autorisés à l’ingestion."""
    configured_settings = settings or Settings.from_environment()

    for source_name in source_names:
        if source_name == "cnf":
            yield from _get_cnf_artifacts(configured_settings.raw_directory)
        elif source_name == "kaggle":
            yield _get_kaggle_artifact(configured_settings.raw_directory)
        elif source_name == "off":
            yield _get_off_artifact(configured_settings.off_file, configured_settings.raw_directory)
        else:
            raise ValueError(f"Unsupported source: {source_name}")


def _get_cnf_artifacts(raw_directory: Path) -> Iterator[RawArtifact]:
    cnf_directory = raw_directory / "cnf-fcen-csv"

    for path in sorted(cnf_directory.glob("*.csv")):
        yield RawArtifact(
            source=CNF_SOURCE,
            path=path,
            relative_path=path.relative_to(raw_directory).as_posix(),
            encoding="utf-8" if path.name in _CNF_UTF8_FILENAMES else "cp1252",
            media_type="text/csv",
        )


def _get_kaggle_artifact(raw_directory: Path) -> RawArtifact:
    path = raw_directory / "kaggle-recipes" / "recipes_extended.json"

    return RawArtifact(
        source=KAGGLE_SOURCE,
        path=path,
        relative_path=path.relative_to(raw_directory).as_posix(),
        encoding="utf-8",
        media_type="application/json",
    )


def _get_off_artifact(off_file: Path, raw_directory: Path) -> RawArtifact:
    """Open Food Facts complet (monde entier) : aucun filtre à cette étape."""
    if not off_file.is_file():
        raise FileNotFoundError(
            f"Open Food Facts TSV not found: {off_file}. "
            "Set ELT_OFF_FILE to the downloaded TSV path."
        )
    try:
        relative_path = off_file.relative_to(raw_directory).as_posix()
    except ValueError:
        relative_path = off_file.name

    return RawArtifact(
        source=OFF_SOURCE,
        path=off_file,
        relative_path=relative_path,
        encoding="utf-8-sig",
        media_type="text/tab-separated-values",
    )