"""Script de recherche sémantique multilingue pour les recettes."""

from __future__ import annotations

from fastembed import TextEmbedding
from qdrant_client import QdrantClient


def test_french_search(user_query: str) -> None:
    client = QdrantClient(host="localhost", port=6333)
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    query_vector = list(embedding_model.embed([user_query]))[0].tolist()

    search_result = client.query_points(collection_name="recipes",query=query_vector,limit=5,)

    if not search_result.points:
        print("Aucun résultat trouvé.")
        return

    for idx, hit in enumerate(search_result.points, start=1):
        payload = hit.payload
        print(f"Top {idx} (Score: {hit.score:.4f}) -> {payload.get('recipe_title')}")
        print(f"  Description: {payload.get('description')}")
        print(f"  Ingrédients: {payload.get('ingredients', [])[:3]}...")
        print("-" * 50)


if __name__ == "__main__":
    test_french_search("recette simple et bonne au goût pour le souper avec du bacon")