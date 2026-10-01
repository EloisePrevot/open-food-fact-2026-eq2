"""Chargement des données brutes vers SQLite et vérification des moteurs."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence

from elt.config import Settings
from elt.connections import DatabaseConnections, open_sqlite_connection
from elt.extract import SUPPORTED_SOURCES, get_raw_artifacts
from elt.raw_extractors import extractor_for
from elt.raw_storage import RawDataStore


def open_load_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs cibles du chargement, sans écrire de données."""
    return DatabaseConnections.connect(settings or Settings.from_environment())


def verify_database_connections(settings: Settings | None = None) -> None:
    """Vérifie SQLite, MongoDB et Qdrant par une opération sans effet de bord."""
    with open_load_connections(settings) as connections:
        connections.verify_connections()


def load_raw_sources(source_names: Sequence[str], settings: Settings | None = None) -> int:
    """Charge les sources brutes désignées dans SQLite, sans toucher MongoDB ni Qdrant."""
    configured_settings = settings or Settings.from_environment()

    with open_sqlite_connection(configured_settings) as connection:
        data_store = RawDataStore(connection)
        data_store.initialize_schema()
        total_record_count = 0

        for artifact in get_raw_artifacts(source_names, configured_settings):
            record_count = data_store.ingest(artifact, extractor_for(artifact).extract(artifact))
            total_record_count += record_count
            print(f"{artifact.relative_path}: {record_count} records loaded")

    return total_record_count


def main() -> None:
    parser = ArgumentParser(description="Commandes du pipeline ELT Open Food Facts Québec.")
    parser.add_argument(
        "--check-connections",
        action="store_true",
        help="vérifie les connexions SQLite, MongoDB et Qdrant",
    )
    parser.add_argument(
        "--load-raw",
        choices=(*SUPPORTED_SOURCES, "all"),
        help="charge les enregistrements bruts CNF et/ou Kaggle vers SQLite",
    )
    arguments = parser.parse_args()

    if arguments.check_connections:
        verify_database_connections()
        print("SQLite, MongoDB and Qdrant connections are available.")
        return

    if arguments.load_raw:
        source_names = SUPPORTED_SOURCES if arguments.load_raw == "all" else (arguments.load_raw,)
        record_count = load_raw_sources(source_names)
        print(f"{record_count} raw records loaded into SQLite.")
        return

    parser.error("Specify --check-connections or --load-raw.")


if __name__ == "__main__":
    main()
