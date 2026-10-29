from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

from pymongo import ASCENDING, ReplaceOne
from pymongo.database import Database

from connections import DatabaseConnections
from load.batching import batched, capped
from load.load_state import LoadState, is_up_to_date, requested_state
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
        products.create_index(
            [("codeBarres", ASCENDING)],
            unique=True,
            partialFilterExpression={"codeBarres": {"$type": "string"}},
        )

    def upsert(self, collection: str, documents: Iterable[dict[str, Any]], loaded_at: str) -> int:
        total = 0
        for batch in batched(documents, BATCH_SIZE):
            self._database[collection].bulk_write(
                [_replace(document, loaded_at) for document in batch], ordered=False
            )
            total += len(batch)
        return total

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
    state = requested_state(connections.postgres, source.raw_source, limit)
    if skip_up_to_date and is_up_to_date(store.load_state(source.label), state):
        print(f"MongoDB : {source.label} déjà à jour, ignoré")
        return {"dejaAJour": 1}
    stats = _load(connections, store, source, limit, loaded_at)
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
    documents = capped(source.documents(connections.postgres, stats), limit)
    stats["charges"] = store.upsert(collection, documents, loaded_at)
    stats["supprimes"] = 0 if limit else store.purge_stale(collection, source.source, loaded_at)
    stats["total"] = store.count(collection, source.source)
    print(f"{source.label} : {dict(stats)}")
    return dict(stats)


def _replace(document: dict[str, Any], loaded_at: str) -> ReplaceOne:
    return ReplaceOne(
        {"_id": document["_id"]}, {**document, "_meta": {"chargeLe": loaded_at}}, upsert=True
    )
