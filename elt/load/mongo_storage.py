from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from pymongo import ASCENDING, ReplaceOne
from pymongo.database import Database

from connections import DatabaseConnections
from load.batching import batched
from load.load_state import LoadState, is_up_to_date, requested_state
from load.progress import CountProgress
from load.stratified_sample import category_of, resolve_limit, stratified_sample
from load.translation_reuse import PREVIOUS_TRANSLATION_FIELDS, reuse_translations
from transform.french_fields import fill_french_fields
from transform.transform import DOCUMENT_SOURCES, PRODUCT, RECIPE, DocumentSource

COLLECTIONS = {RECIPE: "recipes", PRODUCT: "products"}
STATE_COLLECTION = "etat_chargements"
BATCH_SIZE = 1_000


class MongoDataStore:
    def __init__(self, database: Database) -> None:
        self._database = database

    def ensure_collections(self) -> None:
        self._database[COLLECTIONS[RECIPE]].create_index([("type", ASCENDING)])
        products = self._database[COLLECTIONS[PRODUCT]]
        products.create_index([("source", ASCENDING)])
        products.create_index([("cles", ASCENDING)])
        products.create_index([("marques", ASCENDING)])
        products.create_index(
            [("codeBarres", ASCENDING)],
            unique=True,
            partialFilterExpression={"codeBarres": {"$type": "string"}},
        )

    def upsert(
        self,
        collection: str,
        kind: str,
        documents: Iterable[dict[str, Any]],
        loaded_at: str,
        progress: CountProgress | None = None,
        stats: Counter | None = None,
    ) -> int:
        total = 0
        for batch in batched(documents, BATCH_SIZE):
            translated = self._translate(collection, kind, batch, stats)
            self._database[collection].bulk_write(
                [_replace(document, loaded_at) for document in translated], ordered=False
            )
            total += len(batch)
            if progress is not None:
                progress.update(total)
        return total

    def _translate(
        self, collection: str, kind: str, batch: list[dict[str, Any]], stats: Counter | None
    ) -> list[dict[str, Any]]:
        if kind != RECIPE:
            return fill_french_fields(kind, batch)
        reused, pending = reuse_translations(batch, self._previous_translations(collection, batch))
        if stats is not None:
            stats["traductionsReutilisees"] += len(reused)
        return reused + fill_french_fields(kind, pending)

    def _previous_translations(
        self, collection: str, batch: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        ids = [document["_id"] for document in batch]
        cursor = self._database[collection].find({"_id": {"$in": ids}}, PREVIOUS_TRANSLATION_FIELDS)
        return {previous["_id"]: previous for previous in cursor}

    def purge_stale(self, collection: str, source: str, loaded_at: str) -> int:
        stale = {"source": source, "_meta.chargeLe": {"$ne": loaded_at}}
        return self._database[collection].delete_many(stale).deleted_count

    def count(self, collection: str, source: str) -> int:
        return self._database[collection].count_documents({"source": source})

    def load_state(self, label: str) -> LoadState | None:
        return LoadState.from_dict(self._database[STATE_COLLECTION].find_one({"_id": label}))

    def save_load_state(self, label: str, state: LoadState, loaded_at: str) -> None:
        self._database[STATE_COLLECTION].replace_one(
            {"_id": label}, {**state.to_dict(), "chargeLe": loaded_at}, upsert=True
        )


def run_mongo_loads(
    connections: DatabaseConnections, limit: int | None, skip_up_to_date: bool = False
) -> dict[str, dict[str, int]]:
    store = MongoDataStore(connections.mongo_database)
    store.ensure_collections()
    loaded_at = datetime.now(UTC).isoformat()
    return {
        source.label: load_source(connections, store, source, limit, loaded_at, skip_up_to_date)
        for source in DOCUMENT_SOURCES
    }


def load_source(
    connections: DatabaseConnections,
    store: MongoDataStore,
    source: DocumentSource,
    limit: int | None,
    loaded_at: str,
    skip_up_to_date: bool = False,
) -> dict[str, int]:
    source_limit = resolve_limit(source.kind, limit)
    state = requested_state(connections.postgres, source.raw_source, source_limit)
    if skip_up_to_date and is_up_to_date(store.load_state(source.label), state):
        print(f"MongoDB : {source.label} déjà à jour, ignoré")
        return {"dejaAJour": 1}
    stats = _load(connections, store, source, source_limit, loaded_at)
    store.save_load_state(source.label, state, loaded_at)
    return stats


def _load(
    connections: DatabaseConnections,
    store: MongoDataStore,
    source: DocumentSource,
    limit: int | None,
    loaded_at: str,
) -> dict[str, int]:
    print(f"MongoDB : {source.label}...")
    collection = COLLECTIONS[source.kind]
    stats: Counter = Counter()
    total_rows = _source_row_total(connections, source, limit)
    progress = CountProgress(source.label, total_rows)
    documents = stratified_sample(
        source.documents(connections.postgres, stats), limit, category_of(source.kind)
    )
    stats["charges"] = store.upsert(collection, source.kind, documents, loaded_at, progress, stats)
    progress.done(stats["charges"])
    stats["supprimes"] = 0 if limit else store.purge_stale(collection, source.source, loaded_at)
    stats["total"] = store.count(collection, source.source)
    print(f"{source.label} : {dict(stats)}")
    return dict(stats)


def _source_row_total(
    connections: DatabaseConnections, source: DocumentSource, limit: int | None
) -> int:
    """Estime le nombre de documents à charger pour afficher une progression.

    Le total exact après filtrage n'est pas connu d'avance ; on prend le nombre
    de documents réellement conservés lors du dernier chargement comme repère, à
    défaut une valeur neutre. La progression reste indicative mais utile pour
    estimer la durée restante.
    """
    stored = connections.mongo_database[COLLECTIONS[source.kind]].count_documents(
        {"source": source.source}
    )
    if limit:
        return min(stored, limit) if stored else limit
    return stored or 1


def _replace(document: dict[str, Any], loaded_at: str) -> ReplaceOne:
    return ReplaceOne(
        {"_id": document["_id"]}, {**document, "_meta": {"chargeLe": loaded_at}}, upsert=True
    )

