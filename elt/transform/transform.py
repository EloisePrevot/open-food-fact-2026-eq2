"""Transformation: nettoie et met en forme les données extraites."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any

from config import Settings
from connections import DatabaseConnections
from transform.recipe_qdrant_transform import RecipeQdrantTransform
from transform.ingredient_qdrant_transform import IngredientQdrantTransform


def open_transformation_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs nécessaires au rejeu des transformations, sans les exécuter."""
    return DatabaseConnections.connect(settings or Settings.from_environment())


def transform_recipes(connection_factory: Callable[[], DatabaseConnections]) -> Iterator[dict[str, Any]]:
    """Récupère et transforme les données brutes des recettes."""
    with connection_factory() as connections:
        cursor = connections.sqlite.execute(
            """
            SELECT payload_json 
            FROM raw_records 
            WHERE artifact_id IN (
                SELECT artifact_id 
                FROM raw_artifacts 
                WHERE source = 'extended_recipes_dataset'
            )
            """
        )
        for row in cursor:
            raw_payload = json.loads(row[0])
            yield RecipeQdrantTransform.transform(raw_payload)


def transform_ingredients(connection_factory: Callable[[], DatabaseConnections]) -> Iterator[dict[str, Any]]:
    with connection_factory() as connections:
        cursor = connections.sqlite.execute(
            """
            SELECT payload_json 
            FROM raw_records 
            WHERE artifact_id IN (
                SELECT artifact_id 
                FROM raw_artifacts 
                WHERE source = 'canadian_nutrient_file'
            )
            """
        )
        for row in cursor:
            raw_payload = json.loads(row[0])
            yield IngredientQdrantTransform.transform(raw_payload)


def run_all_transformations(settings: Settings | None = None) -> dict[str, list[dict[str, Any]]]:
    connection_factory = lambda: open_transformation_connections(settings)

    return {
        "recipes": list(transform_recipes(connection_factory)),
        "ingredients": list(transform_ingredients(connection_factory)),
    }