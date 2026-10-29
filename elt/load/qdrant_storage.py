from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm

from connections import DatabaseConnections
from load.batching import batched
from load.load_state import LoadState, is_up_to_date, requested_state
from load.stratified_sample import category_of, resolve_limit, stratified_sample
from transform.transform import DOCUMENT_SOURCES, PRODUCT, RECIPE, DocumentSource
from transform.values import NUTRI_SCORE_GRADES

COLLECTIONS = {RECIPE: "recipes", PRODUCT: "ingredients"}
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
VECTOR_SIZE = 384
BATCH_SIZE = 64
FINGERPRINT_FIELD = "empreinte"
SCROLL_SIZE = 10_000
PURGE_BATCH_SIZE = 1_000

PAYLOAD_INDEXES = {
    RECIPE: {"type": models.PayloadSchemaType.KEYWORD},
    PRODUCT: {
        "produitDeBase": models.PayloadSchemaType.BOOL,
        "marques": models.PayloadSchemaType.KEYWORD,
        "nutriScore": models.PayloadSchemaType.KEYWORD,
        "nova": models.PayloadSchemaType.INTEGER,
    },
}


@dataclass(frozen=True)
class PreparedPoint:
    id: str
    text: str
    payload: dict[str, Any]

    def has_same_text(self, existing_payload: dict[str, Any] | None) -> bool:
        return existing_payload is not None and existing_payload.get(FINGERPRINT_FIELD) == self.payload[FINGERPRINT_FIELD]


def _prepare(collection: str, point: dict[str, Any]) -> PreparedPoint:
    return PreparedPoint(
        id=str(uuid5(NAMESPACE_URL, f"{collection}:{point['id']}")),
        text=point["text"],
        payload={**point["payload"], FINGERPRINT_FIELD: _fingerprint(point["text"])},
    )


def _fingerprint(text: str) -> str:
    return hashlib.sha256(f"{EMBEDDING_MODEL}\n{text}".encode()).hexdigest()[:16]


def _overwrites(points: list[PreparedPoint]) -> list[models.OverwritePayloadOperation]:
    return [
        models.OverwritePayloadOperation(
            overwrite_payload=models.SetPayload(payload=point.payload, points=[point.id])
        )
        for point in points
    ]


class QdrantDataStore:
    def __init__(self, client: QdrantClient, embedding_model: Any | None = None) -> None:
        self.client = client
        self.embedding_model = embedding_model or TextEmbedding(model_name=EMBEDDING_MODEL)
        self._loaded_ids: defaultdict[str, set[str]] = defaultdict(set)

    def ensure_collections(self) -> None:
        existing = {collection.name for collection in self.client.get_collections().collections}
        for kind, name in COLLECTIONS.items():
            if name not in existing:
                self._create_collection(name)
            self._create_payload_indexes(name, PAYLOAD_INDEXES[kind])

    def upsert(self, kind: str, points: Iterable[dict[str, Any]]) -> Counter:
        collection = COLLECTIONS[kind]
        stats = Counter(vectorises=0, inchanges=0)
        with tqdm(desc=f"Indexation {collection}", unit="docs") as progress:
            for batch in batched(points, BATCH_SIZE):
                stats.update(self._upsert_batch(collection, [_prepare(collection, point) for point in batch]))
                progress.update(len(batch))
        return stats

    def _upsert_batch(self, collection: str, points: list[PreparedPoint]) -> Counter:
        existing = self._existing_payloads(collection, points)
        to_embed = [point for point in points if not point.has_same_text(existing.get(point.id))]
        to_refresh = [
            point for point in points if point not in to_embed and existing[point.id] != point.payload
        ]
        if to_embed:
            self.client.upsert(collection_name=collection, points=self._embed(to_embed))
        if to_refresh:
            self.client.batch_update_points(collection_name=collection, update_operations=_overwrites(to_refresh))
        self._loaded_ids[collection].update(point.id for point in points)
        return Counter(vectorises=len(to_embed), inchanges=len(points) - len(to_embed))

    def _existing_payloads(self, collection: str, points: list[PreparedPoint]) -> dict[str, dict[str, Any]]:
        records = self.client.retrieve(
            collection_name=collection,
            ids=[point.id for point in points],
            with_payload=True,
            with_vectors=False,
        )
        return {str(record.id): record.payload or {} for record in records}

    def load_state(self, kind: str, label: str) -> LoadState | None:
        return LoadState.from_dict(self._metadata(COLLECTIONS[kind]).get(label))

    def save_load_state(self, kind: str, label: str, state: LoadState) -> None:
        collection = COLLECTIONS[kind]
        metadata = {**self._metadata(collection), label: state.to_dict()}
        self.client.update_collection(collection_name=collection, metadata=metadata)

    def _metadata(self, collection: str) -> dict[str, Any]:
        return self.client.get_collection(collection).config.metadata or {}

    def purge_unloaded(self, excluded: Collection[str] = ()) -> dict[str, int]:
        return {
            collection: self._purge(collection)
            for collection in COLLECTIONS.values()
            if collection not in excluded
        }

    def _purge(self, collection: str) -> int:
        loaded = self._loaded_ids[collection]
        stale = [point_id for point_id in self._point_ids(collection) if str(point_id) not in loaded]
        for batch in batched(stale, PURGE_BATCH_SIZE):
            self.client.delete(
                collection_name=collection,
                points_selector=models.PointIdsList(points=batch),
                wait=True,
            )
        return len(stale)

    def _point_ids(self, collection: str) -> Iterator[models.ExtendedPointId]:
        offset = None
        while True:
            records, offset = self.client.scroll(
                collection_name=collection,
                limit=SCROLL_SIZE,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )
            yield from (record.id for record in records)
            if offset is None:
                return

    def search_recipes(
        self, description: str, *, limit: int = 10, recipe_type: str | None = None
    ) -> models.QueryResponse:
        conditions = [_match("type", recipe_type)] if recipe_type else []
        return self._search(RECIPE, description, conditions, limit)

    def search_products(
        self,
        ingredient: str,
        *,
        limit: int = 10,
        basic_food: bool | None = None,
        brand: str | None = None,
        nutri_score_min: str | None = None,
        nova_max: int | None = None,
    ) -> models.QueryResponse:
        conditions = product_conditions(basic_food, brand, nutri_score_min, nova_max)
        return self._search(PRODUCT, ingredient, conditions, limit)

    def _search(
        self, kind: str, query: str, conditions: list[models.FieldCondition], limit: int
    ) -> models.QueryResponse:
        return self.client.query_points(
            collection_name=COLLECTIONS[kind],
            query=self._vector(query),
            query_filter=models.Filter(must=conditions) if conditions else None,
            limit=limit,
            with_payload=True,
        )

    def _create_collection(self, name: str) -> None:
        # Vecteurs et index HNSW stockés sur disque (memory-map) plutôt qu'en RAM.
        # Le conteneur partage ~8 Gio avec la JVM, Postgres, Mongo et le modèle
        # d'embeddings ; garder ~65 000 vecteurs 384-D hors du tas évite un
        # dépassement mémoire (OOM) à l'indexation, au prix d'une latence accrue,
        # acceptable pour une preuve de concept.
        self.client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
                on_disk=True,
                hnsw_config=models.HnswConfigDiff(on_disk=True),
            ),
        )

    def _create_payload_indexes(self, name: str, indexes: dict[str, models.PayloadSchemaType]) -> None:
        for field, schema in indexes.items():
            self.client.create_payload_index(
                collection_name=name, field_name=field, field_schema=schema, wait=True
            )

    def _embed(self, points: list[PreparedPoint]) -> list[models.PointStruct]:
        vectors = self.embedding_model.embed([point.text for point in points])
        return [
            models.PointStruct(id=point.id, vector=vector.tolist(), payload=point.payload)
            for point, vector in zip(points, vectors, strict=True)
        ]

    def _vector(self, text: str) -> list[float]:
        return next(iter(self.embedding_model.embed([text]))).tolist()


def product_conditions(
    basic_food: bool | None, brand: str | None, nutri_score_min: str | None, nova_max: int | None
) -> list[models.FieldCondition]:
    conditions = []
    if basic_food is not None:
        conditions.append(_match("produitDeBase", basic_food))
    if brand:
        conditions.append(_match("marques", brand.strip().casefold()))
    if nutri_score_min:
        conditions.append(_match_any("nutriScore", grades_at_least(nutri_score_min)))
    if nova_max is not None:
        conditions.append(models.FieldCondition(key="nova", range=models.Range(lte=nova_max)))
    return conditions


def grades_at_least(minimum: str) -> list[str]:
    grade = minimum.casefold()
    if grade not in NUTRI_SCORE_GRADES:
        raise ValueError("nutri_score_min must be one of A, B, C, D or E.")
    return list(NUTRI_SCORE_GRADES[: NUTRI_SCORE_GRADES.index(grade) + 1])


def run_qdrant_loads(
    connections: DatabaseConnections, limit: int | None, skip_up_to_date: bool = False
) -> dict[str, dict[str, int]]:
    store = QdrantDataStore(connections.qdrant)
    store.ensure_collections()
    summary = {
        source.label: load_source(connections, store, source, limit, skip_up_to_date)
        for source in DOCUMENT_SOURCES
    }
    if limit is None:
        summary["supprimes"] = store.purge_unloaded(_skipped_collections(summary))
    return summary


def load_source(
    connections: DatabaseConnections,
    store: QdrantDataStore,
    source: DocumentSource,
    limit: int | None,
    skip_up_to_date: bool = False,
) -> dict[str, int]:
    source_limit = resolve_limit(source.kind, limit)
    state = requested_state(connections.postgres, source.raw_source, source_limit, EMBEDDING_MODEL)
    if skip_up_to_date and is_up_to_date(store.load_state(source.kind, source.label), state):
        print(f"Qdrant : {source.label} déjà à jour, ignoré")
        return {"dejaAJour": 1}
    stats = _load(connections, store, source, source_limit)
    store.save_load_state(source.kind, source.label, state)
    return stats


def _load(
    connections: DatabaseConnections,
    store: QdrantDataStore,
    source: DocumentSource,
    limit: int | None,
) -> dict[str, int]:
    print(f"Qdrant : {source.label}...")
    stats: Counter = Counter()
    documents = stratified_sample(
        source.documents(connections.postgres, stats), limit, category_of(source.kind)
    )
    stats.update(store.upsert(source.kind, map(source.to_point, documents)))
    return dict(stats)


def _skipped_collections(summary: dict[str, dict[str, int]]) -> set[str]:
    return {
        COLLECTIONS[source.kind] for source in DOCUMENT_SOURCES if "dejaAJour" in summary[source.label]
    }


def _match(key: str, value: Any) -> models.FieldCondition:
    return models.FieldCondition(key=key, match=models.MatchValue(value=value))


def _match_any(key: str, values: list[str]) -> models.FieldCondition:
    return models.FieldCondition(key=key, match=models.MatchAny(any=values))
