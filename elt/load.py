"""Chargement des données brutes vers PostgreSQL et vérification des moteurs."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence

from elt.config import Settings
from elt.connections import DatabaseConnections, open_postgres_connection
from elt.extract import SUPPORTED_SOURCES, get_raw_artifacts
from elt.off_storage import load_off_north_america
from elt.raw_extractors import extractor_for
from elt.raw_storage import RawDataStore

OFF_SOURCE = "off"


def open_load_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs cibles du chargement, sans écrire de données."""
    return DatabaseConnections.connect(settings or Settings.from_environment())


def verify_database_connections(settings: Settings | None = None) -> None:
    """Vérifie PostgreSQL, MongoDB et Qdrant par une opération sans effet de bord."""
    with open_load_connections(settings) as connections:
        connections.verify_connections()


def load_raw_sources(source_names: Sequence[str], settings: Settings | None = None) -> int:
    """Charge les sources brutes désignées dans PostgreSQL, sans toucher MongoDB ni Qdrant."""
    configured_settings = settings or Settings.from_environment()

    with open_postgres_connection(configured_settings) as connection:
        data_store = RawDataStore(connection)
        data_store.initialize_schema()
        total_record_count = 0

        for artifact in get_raw_artifacts(source_names, configured_settings):
            record_count = data_store.ingest(artifact, extractor_for(artifact).extract(artifact))
            total_record_count += record_count
            print(f"{artifact.relative_path}: {record_count} records loaded")

        # Les index sont créés après le chargement pour accélérer le COPY.
        data_store.create_indexes()

    return total_record_count


def load_off_products(settings: Settings | None = None) -> int:
    """Charge off.csv côté serveur et ne garde que les produits nord-américains."""
    configured_settings = settings or Settings.from_environment()
    off_csv_path = configured_settings.raw_directory / "off.csv"

    with open_postgres_connection(configured_settings) as connection:
        return load_off_north_america(connection, off_csv_path)


def main() -> None:
    parser = ArgumentParser(description="Commandes du pipeline ELT Open Food Facts Québec.")
    parser.add_argument(
        "--check-connections",
        action="store_true",
        help="vérifie les connexions PostgreSQL, MongoDB et Qdrant",
    )
    parser.add_argument(
        "--load-raw",
        choices=(*SUPPORTED_SOURCES, "all"),
        help="charge les enregistrements bruts CNF et/ou Kaggle vers PostgreSQL",
    )
    parser.add_argument(
        "--load-off",
        action="store_true",
        help=(
            "charge off.csv via COPY côté serveur et ne garde que les produits "
            "nord-américains (nécessite le volume ./elt/raw monté dans le conteneur)"
        ),
    )
    arguments = parser.parse_args()

    if arguments.check_connections:
        verify_database_connections()
        print("PostgreSQL, MongoDB and Qdrant connections are available.")
        return

    if arguments.load_raw:
        source_names = SUPPORTED_SOURCES if arguments.load_raw == "all" else (arguments.load_raw,)
        record_count = load_raw_sources(source_names)
        print(f"{record_count} raw records loaded into PostgreSQL.")
        return

    if arguments.load_off:
        kept_count = load_off_products()
        print(f"{kept_count} North American Open Food Facts products loaded into PostgreSQL.")
        return

    parser.error("Specify --check-connections, --load-raw or --load-off.")


if __name__ == "__main__":
    main()
