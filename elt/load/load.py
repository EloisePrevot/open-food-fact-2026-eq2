from __future__ import annotations

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence

from config import Settings
from connections import DatabaseConnections, open_postgres_connection
from extract.extract import SUPPORTED_SOURCES, get_raw_artifacts
from extract.raw_extractors import extractor_for
from load.mongo_storage import run_mongo_loads
from load.postgres_sample import SAMPLE_DATABASE, export_postgres_sample
from load.qdrant_snapshots import export_snapshots
from load.qdrant_storage import run_qdrant_loads
from raw_models import RawArtifact
from raw_storage import RawDataStore


def verify_database_connections(settings: Settings) -> None:
    with DatabaseConnections.connect(settings) as connections:
        connections.verify_connections()
    print("PostgreSQL, MongoDB and Qdrant connections are available.")


def load_raw_sources(source_names: Sequence[str], settings: Settings) -> int:
    with open_postgres_connection(settings) as connection:
        data_store = RawDataStore(connection)
        data_store.initialize_schema()
        total = sum(_ingest(data_store, artifact) for artifact in get_raw_artifacts(source_names, settings))
        data_store.create_indexes()
        return total


def load_mongo(limit: int | None, skip_up_to_date: bool, settings: Settings) -> dict[str, dict[str, int]]:
    with DatabaseConnections.connect(settings) as connections:
        return run_mongo_loads(connections, limit, skip_up_to_date)


def load_qdrant(limit: int | None, skip_up_to_date: bool, settings: Settings) -> dict[str, dict[str, int]]:
    with DatabaseConnections.connect(settings) as connections:
        return run_qdrant_loads(connections, limit, skip_up_to_date)


def export_qdrant_snapshots(settings: Settings) -> None:
    with DatabaseConnections.connect(settings) as connections:
        manifest = export_snapshots(connections.qdrant, settings.qdrant_url, settings.snapshot_directory)
    print(f"Snapshots Qdrant exportés : {manifest.read_text(encoding='utf-8')}")


def export_postgres_sample_database(settings: Settings) -> None:
    with DatabaseConnections.connect(settings) as connections:
        summary = export_postgres_sample(settings, connections.mongo_database)
    print(f"Échantillon brut copié dans la base {SAMPLE_DATABASE} : {summary}")


def _ingest(data_store: RawDataStore, artifact: RawArtifact) -> int:
    record_count = data_store.ingest(artifact, extractor_for(artifact).extract(artifact))
    if record_count is None:
        print(f"{artifact.relative_path}: déjà dans PostgreSQL (contenu identique), ignoré")
        return 0
    print(f"{artifact.relative_path}: {record_count} records loaded")
    return record_count


def _parse_arguments() -> tuple[ArgumentParser, Namespace]:
    parser = ArgumentParser(description="Commandes du pipeline ELT Open Food Facts Québec.")
    parser.add_argument("--check-connections", action="store_true", help="vérifie PostgreSQL, MongoDB et Qdrant")
    parser.add_argument(
        "--load-raw", choices=(*SUPPORTED_SOURCES, "all"), help="charge les sources brutes dans PostgreSQL"
    )
    parser.add_argument("--load-mongo", action="store_true", help="nettoie PostgreSQL vers MongoDB")
    parser.add_argument("--load-qdrant", action="store_true", help="indexe PostgreSQL dans Qdrant")
    parser.add_argument(
        "--export-qdrant-snapshots", action="store_true", help="exporte les collections Qdrant en snapshots"
    )
    parser.add_argument(
        "--export-postgres-sample",
        action="store_true",
        help="copie le brut de l'échantillon servi par MongoDB dans une base à publier",
    )
    parser.add_argument(
        "--limit", type=int, default=1000, help="documents maximum par source (0 = aucune limite)"
    )
    parser.add_argument(
        "--skip-up-to-date",
        action="store_true",
        help="ignore une source déjà chargée avec les mêmes données brutes et règles",
    )
    return parser, parser.parse_args()


def main() -> None:
    parser, arguments = _parse_arguments()
    settings = Settings.from_environment()
    limit = arguments.limit if arguments.limit > 0 else None

    if arguments.check_connections:
        verify_database_connections(settings)
    elif arguments.load_raw:
        sources = SUPPORTED_SOURCES if arguments.load_raw == "all" else (arguments.load_raw,)
        print(f"{load_raw_sources(sources, settings)} raw records loaded into PostgreSQL.")
    elif arguments.load_mongo:
        print(f"MongoDB load completed. Summary: {load_mongo(limit, arguments.skip_up_to_date, settings)}")
    elif arguments.load_qdrant:
        print(f"Qdrant load completed. Summary: {load_qdrant(limit, arguments.skip_up_to_date, settings)}")
    elif arguments.export_qdrant_snapshots:
        export_qdrant_snapshots(settings)
    elif arguments.export_postgres_sample:
        export_postgres_sample_database(settings)
    else:
        parser.error(
            "Specify --check-connections, --load-raw, --load-mongo, --load-qdrant, "
            "--export-qdrant-snapshots, or --export-postgres-sample."
        )


if __name__ == "__main__":
    main()
