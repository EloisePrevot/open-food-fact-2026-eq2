"""Chargement des données brutes vers SQLite et vérification des moteurs."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Callable, Sequence
from itertools import islice

from config import Settings
from connections import DatabaseConnections, open_sqlite_connection
from extract.extract import SUPPORTED_SOURCES, get_raw_artifacts
from extract.raw_extractors import extractor_for
from raw_storage import RawDataStore
from load.qdrant_storage import QdrantDataStore
from transform.transform import transform_recipes, transform_ingredients


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


def load_recipes_to_qdrant(
    connection_factory: Callable[[], DatabaseConnections],
    limit: int | None = 1000,
    settings: Settings | None = None
) -> int:
    """Récupère les recettes transformées et les charge dans Qdrant avec une limite."""
    print("⏳ Étape 1/2 : Récupération et transformation des recettes...")

    generator = transform_recipes(connection_factory)

    # Si une limite est définie, on coupe le flux proprement, sinon on stream tout
    if limit is not None and limit > 0:
        documents = list(islice(generator, limit))
    else:
        documents = generator  # Mode streaming complet si limit=0

    with connection_factory() as connections:
        qdrant_store = QdrantDataStore(connections.qdrant)
        qdrant_store.ensure_collections()
        qdrant_store.load_recipes(documents)

    count = len(documents) if isinstance(documents, list) else "toutes les"
    print(f"✅ {count} recettes chargées avec succès dans Qdrant.")
    return len(documents) if isinstance(documents, list) else 0


def load_ingredients_to_qdrant(
    connection_factory: Callable[[], DatabaseConnections],
    limit: int | None = 1000,
    settings: Settings | None = None
) -> int:
    """Récupère les ingrédients transformés et les charge dans Qdrant avec une limite."""
    print("\n⏳ Étape 2/2 : Récupération et transformation des ingrédients...")

    generator = transform_ingredients(connection_factory)

    if limit is not None and limit > 0:
        documents = list(islice(generator, limit))
    else:
        documents = generator

    with connection_factory() as connections:
        qdrant_store = QdrantDataStore(connections.qdrant)
        qdrant_store.ensure_collections()
        qdrant_store.load_ingredients(documents)

    count = len(documents) if isinstance(documents, list) else "tous les"
    print(f"✅ {count} ingrédients chargés avec succès dans Qdrant.")
    return len(documents) if isinstance(documents, list) else 0


def run_all_loads(limit: int | None = 1000, settings: Settings | None = None) -> dict[str, int]:
    """Fonction orchestrant l'ensemble des chargements vers Qdrant avec une limite."""
    connection_factory = lambda: open_load_connections(settings)

    recipes_count = load_recipes_to_qdrant(connection_factory, limit=limit, settings=settings)
    ingredients_count = load_ingredients_to_qdrant(connection_factory, limit=limit, settings=settings)

    return {
        "recipes_loaded": recipes_count,
        "ingredients_loaded": ingredients_count,
    }


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
    parser.add_argument(
        "--load-qdrant",
        action="store_true",
        help="Transforme SQLite vers QDRANT",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre maximal de documents à charger (Défaut: 1000. Mettre 0 pour tout charger sans limite).",
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

    if arguments.load_qdrant:
        # Si --limit 0 est passé, on le convertit en None pour désactiver la limite
        effective_limit = None if arguments.limit <= 0 else arguments.limit
        results = run_all_loads(limit=effective_limit)
        print(f"\nQdrant load completed successfully. Summary: {results}")
        return

    parser.error("Specify --check-connections, --load-raw, or --load-qdrant.")


if __name__ == "__main__":
    main()