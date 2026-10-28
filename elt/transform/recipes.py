from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter
from collections.abc import Iterator
from typing import Any

from extract.extract import KAGGLE_SOURCE
from transform.ingredient_identity import ingredient_key
from transform.raw_records import RawRow, clean_rows, iter_raw_rows
from transform.values import json_list, optional_text, text, text_list, to_bool, to_int

SOURCE = "kaggle"

_DIET_FIELDS = {
    "is_vegan": "vegan",
    "is_vegetarian": "vegetarien",
    "is_halal": "halal",
    "is_kosher": "casher",
    "is_nut_free": "sansNoix",
    "is_dairy_free": "sansLactose",
    "is_gluten_free": "sansGluten",
}


def recipe_documents(sqlite: sqlite3.Connection, stats: Counter) -> Iterator[dict[str, Any]]:
    rows = iter_raw_rows(sqlite, KAGGLE_SOURCE, "recipes_extended.json")
    return clean_rows(rows, clean_recipe, stats)


def clean_recipe(row: RawRow) -> dict[str, Any] | None:
    raw = row.payload
    title = text(raw.get("recipe_title") or raw.get("title"))
    ingredients = recipe_ingredients(raw)
    if not title or not ingredients:
        return None

    directions = json_list(raw.get("directions") or raw.get("directions_raw"))
    category = optional_text(raw.get("category"))
    identifiant = f"recipe:{recipe_id(raw, title, ingredients, directions)}"
    return {
        "_id": identifiant,
        "identifiant": identifiant,
        "source": SOURCE,
        "nom": title,
        "description": text(raw.get("description")),
        "type": recipe_types(raw, category),
        "categorie": category,
        "sousCategorie": optional_text(raw.get("subcategory")),
        "nbIngredients": len(ingredients),
        "ingredients": ingredients,
        "nbEtapes": len(directions),
        "etapes": [str(step) for step in directions],
        "portions": to_int(raw.get("servings")),
        "gouts": text_list(raw.get("tastes")),
        "goutPrincipal": optional_text(raw.get("primary_taste")),
        "goutSecondaire": optional_text(raw.get("secondary_taste")),
        "cuisines": text_list(raw.get("cuisine_list")),
        "vitesseCuisson": optional_text(raw.get("cook_speed")),
        "minutesPreparation": to_int(raw.get("est_prep_time_min")),
        "minutesCuisson": to_int(raw.get("est_cook_time_min")),
        "difficulte": optional_text(raw.get("difficulty")),
        "scoreSante": to_int(raw.get("healthiness_score")),
        "niveauSante": optional_text(raw.get("health_level")),
        "ingredientPrincipal": optional_text(raw.get("main_ingredient")),
        "profilDietetique": text_list(raw.get("dietary_profile")),
        "regime": {french: to_bool(raw.get(english)) for english, french in _DIET_FIELDS.items()},
        "refBrut": row.reference(),
    }


def recipe_ingredients(raw: dict[str, Any]) -> list[dict[str, str]]:
    originals = json_list(raw.get("ingredients") or raw.get("ingredients_raw"))
    canonicals = json_list(raw.get("ingredients_canonical"))
    ingredients = []
    for index, original in enumerate(originals):
        original_text = text(original)
        name = text(canonicals[index]) if index < len(canonicals) else original_text
        if name:
            ingredients.append(
                {"nom": name, "cle": ingredient_key(name), "texteOriginal": original_text}
            )
    return ingredients


def recipe_types(raw: dict[str, Any], category: str | None) -> list[str]:
    courses = text_list(raw.get("course_list"))
    if courses:
        return courses
    return [category] if category else []


def recipe_id(
    raw: dict[str, Any], title: str, ingredients: list[dict[str, str]], directions: list[Any]
) -> str:
    source_id = text(raw.get("recipe_id") or raw.get("id"))
    return source_id or _content_hash(title, ingredients, directions)


def _content_hash(title: str, ingredients: list[dict[str, str]], directions: list[Any]) -> str:
    identity = json.dumps(
        {
            "title": title.casefold(),
            "ingredients": [ingredient["nom"].casefold() for ingredient in ingredients],
            "directions": directions,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()
