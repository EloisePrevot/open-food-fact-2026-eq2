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
from transform.french_fields import fill_french_fields
from transform.transform import DOCUMENT_SOURCES, PRODUCT, RECIPE, DocumentSource

COLLECTIONS = {RECIPE: "recipes", PRODUCT: "products"}
RAW_COLLECTION = "donnees_brutes"
STATE_COLLECTION = "etat_chargements"
RAW_PAYLOAD_FIELD = "_chargeBrute"
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
        self._database[RAW_COLLECTION].create_index([("source", ASCENDING)])

    def upsert(
        self,
        collection: str,
        kind: str,
        documents: Iterable[dict[str, Any]],
        loaded_at: str,
        progress: CountProgress | None = None,
    ) -> int:
        total = 0
        for batch in batched(documents, BATCH_SIZE):
            translated = fill_french_fields(kind, batch)
            served = [_split_raw_payload(document, loaded_at) for document in translated]
            self._database[collection].bulk_write(
                [_replace(document, loaded_at) for document, _ in served], ordered=False
            )
            raw = [raw_document for _, raw_document in served if raw_document is not None]
            if raw:
                self._database[RAW_COLLECTION].bulk_write(
                    [_replace_raw(raw_document) for raw_document in raw], ordered=False
                )
            total += len(batch)
            if progress is not None:
                progress.update(total)
        return total

    def purge_stale(self, collection: str, source: str, loaded_at: str) -> int:
        stale = {"source": source, "_meta.chargeLe": {"$ne": loaded_at}}
        deleted = self._database[collection].delete_many(stale).deleted_count
        self._database[RAW_COLLECTION].delete_many(stale)
        return deleted

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
    stats["charges"] = store.upsert(collection, source.kind, documents, loaded_at, progress)
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


def _split_raw_payload(
    document: dict[str, Any], loaded_at: str
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Sépare la charge brute du document servi.

    Le document retourné en premier est allégé (sans la charge brute) et destiné
    aux collections ``products``/``recipes``. Le second, s'il existe, est
    l'enregistrement brut destiné à la collection ``donnees_brutes``.
    """
    payload = document.pop(RAW_PAYLOAD_FIELD, None)
    if payload is None:
        return document, None
    raw_document = {
        "_id": document["_id"],
        "identifiant": document["identifiant"],
        "source": document["source"],
        "dateIngestion": loaded_at,
        "chargeUtile": payload,
        "_meta": {"chargeLe": loaded_at},
    }
    return document, raw_document


def _replace_raw(raw_document: dict[str, Any]) -> ReplaceOne:
    return ReplaceOne({"_id": raw_document["_id"]}, raw_document, upsert=True)
