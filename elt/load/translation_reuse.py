from __future__ import annotations

from typing import Any

_SCALAR_FIELDS = (("nom", "nomEn"), ("description", "descriptionEn"))
PREVIOUS_TRANSLATION_FIELDS = {"nom": 1, "nomEn": 1, "description": 1, "descriptionEn": 1, "ingredients": 1}


def reuse_translations(
    documents: list[dict[str, Any]], previous_by_id: dict[str, dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    reused: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for document in documents:
        translated = _reuse(document, previous_by_id.get(document["_id"]))
        if translated is None:
            pending.append(document)
        else:
            reused.append(translated)
    return reused, pending


def _reuse(document: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any] | None:
    if previous is None:
        return None
    result = dict(document)
    for french_field, english_field in _SCALAR_FIELDS:
        if not _reuse_scalar(result, previous, french_field, english_field):
            return None
    ingredients = _reuse_ingredients(document.get("ingredients"), previous.get("ingredients"))
    if ingredients is None:
        return None
    if ingredients:
        result["ingredients"] = ingredients
    return result


def _reuse_scalar(
    result: dict[str, Any], previous: dict[str, Any], french_field: str, english_field: str
) -> bool:
    text = result.get(french_field)
    if not _translatable(text):
        return previous.get(french_field) == text
    if previous.get(english_field) != text or not isinstance(previous.get(french_field), str):
        return False
    result[english_field] = text
    result[french_field] = previous[french_field]
    return True


def _reuse_ingredients(current: Any, previous: Any) -> list[dict[str, Any]] | None:
    if not isinstance(current, list):
        return []
    if not isinstance(previous, list) or len(previous) != len(current):
        return None
    reused = [_reuse_ingredient(ingredient, old) for ingredient, old in zip(current, previous)]
    return None if any(ingredient is None for ingredient in reused) else reused


def _reuse_ingredient(ingredient: Any, previous: Any) -> dict[str, Any] | None:
    if not isinstance(ingredient, dict) or not _translatable(ingredient.get("nom")):
        return ingredient
    if not isinstance(previous, dict) or previous.get("nomEn") != ingredient["nom"]:
        return None
    if not isinstance(previous.get("nom"), str):
        return None
    return {**ingredient, "nom": previous["nom"], "nomEn": ingredient["nom"]}


def _translatable(text: Any) -> bool:
    return isinstance(text, str) and bool(text.strip())
