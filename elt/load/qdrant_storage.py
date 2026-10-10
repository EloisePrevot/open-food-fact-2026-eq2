"""Gestion du stockage et de l'indexation vectorielle dans Qdrant avec FastEmbed."""

from __future__ import annotations

from typing import Iterable
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm


class QdrantDataStore:
    def __init__(self, client: QdrantClient) -> None:
        self.client = client
        self.RECIPE_COLLECTION = "recipes"
        self.INGREDIENT_COLLECTION = "ingredients"

        self.embedding_model = TextEmbedding(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

    def ensure_collections(self) -> None:
        vector_size = 384
        collections = {
            self.RECIPE_COLLECTION,
            self.INGREDIENT_COLLECTION,
        }
        existing = {c.name for c in self.client.get_collections().collections}

        for collection_name in collections:
            if collection_name not in existing:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )

    def load_recipes(self, documents: Iterable[dict], batch_size: int = 64) -> None:
        """Charge les recettes vectorisées dans Qdrant par lots."""
        self._upsert_documents(self.RECIPE_COLLECTION, documents, batch_size=batch_size)

    def load_ingredients(self, documents: Iterable[dict], batch_size: int = 64) -> None:
        """Charge les ingrédients vectorisés dans Qdrant par lots."""
        self._upsert_documents(self.INGREDIENT_COLLECTION, documents, batch_size=batch_size)

    def _upsert_documents(
        self, collection_name: str, documents: Iterable[dict], batch_size: int = 64
    ) -> None:
        batch_docs: list[dict] = []
        global_idx = 0

        pbar = tqdm(desc=f"Indexation {collection_name}", unit="docs")

        for doc in documents:
            batch_docs.append(doc)

            if len(batch_docs) >= batch_size:
                self._process_and_upsert_batch(collection_name, batch_docs, global_idx)
                global_idx += len(batch_docs)
                pbar.update(len(batch_docs))
                batch_docs.clear()


        if batch_docs:
            self._process_and_upsert_batch(collection_name, batch_docs, global_idx)
            pbar.update(len(batch_docs))

        pbar.close()

    def _process_and_upsert_batch(
        self, collection_name: str, batch_docs: list[dict], start_idx: int
    ) -> None:
        texts = [doc["text"] for doc in batch_docs]
        payloads = [doc["payload"] for doc in batch_docs]

        vectors = list(self.embedding_model.embed(texts))
        points = [
            models.PointStruct(
                id=start_idx + idx + 1,
                vector=vector.tolist(),
                payload=payload,
            )
            for idx, (vector, payload) in enumerate(zip(vectors, payloads))
        ]

        self.client.upsert(
            collection_name=collection_name,
            points=points,
        )