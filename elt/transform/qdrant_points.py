from __future__ import annotations

from typing import Any

from transform.values import join_words


def recipe_point(recipe: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": recipe["identifiant"],
        "text": recipe_search_text(recipe),
        "payload": {"identifiant": recipe["identifiant"], "type": recipe["type"]},
    }


def product_point(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": product["identifiant"],
        "text": product_search_text(product),
        "payload": {
            "identifiant": product["identifiant"],
            "produitDeBase": product["produitDeBase"],
            "marques": [brand.casefold() for brand in product["marques"]],
            "nutriScore": product["nutriScore"],
            "nova": product["nova"],
        },
    }


def recipe_search_text(recipe: dict[str, Any]) -> str:
    return join_words(
        recipe["nom"],
        recipe["categorie"] or "",
        recipe["description"],
        recipe["difficulte"] or "",
        recipe["vitesseCuisson"] or "",
        " ".join(recipe["gouts"]),
        " ".join(ingredient["nom"] for ingredient in recipe["ingredients"]),
    )


def product_search_text(product: dict[str, Any]) -> str:
    return join_words(
        product["nomProduit"],
        product.get("nomEn") or "",
        product.get("nomGenerique") or "",
        " ".join(product["marques"]),
        " ".join(product.get("categories") or [product["categorie"] or ""]),
        product.get("ingredientsTexte") or "",
    )
