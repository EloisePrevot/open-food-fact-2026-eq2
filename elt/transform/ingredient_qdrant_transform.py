"""Transformation: nettoie et met en forme les données des ingrédients pour Qdrant."""

from __future__ import annotations

from typing import Any


class IngredientQdrantTransform:
    @staticmethod
    def transform(ingredient: dict[str, Any]) -> dict[str, Any]:
        product_name = (
            ingredient.get("product_name")
            or ingredient.get("FoodDescription")
            or ""
        )
        brands = ingredient.get("brands") or ""
        categories = (
            ingredient.get("categories_en")
            or ingredient.get("FoodGroupName")
            or ""
        )
        ingredients_text = ingredient.get("ingredients_text") or ""

        text = " ".join([
            str(product_name),
            str(brands),
            str(categories),
            str(ingredients_text),
        ])

        return {
            "text": text.strip(),
            "payload": ingredient,
        }