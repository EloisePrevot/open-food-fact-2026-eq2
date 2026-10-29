"""Remplissage des champs français des documents, par lots.

Seules les recettes sont traduites : leur titre et leur description viennent d'un
corpus anglais et sont montrés à l'utilisateur. Le nom anglais d'origine est
toujours conservé (``nomEn``, ``descriptionEn``). Les noms de produits ne sont
pas traduits (voir ``_TRANSLATABLE_FIELDS``) : l'appariement repose sur les
embeddings multilingues, pas sur le nom français.
"""

from __future__ import annotations

from typing import Any

from transform.transform import PRODUCT, RECIPE
from transform.translation import translate_to_french

# Pour chaque genre de document : (champ source anglais, champ français, champ anglais conservé).
_TRANSLATABLE_FIELDS: dict[str, tuple[tuple[str, str, str], ...]] = {
    RECIPE: (
        ("nom", "nom", "nomEn"),
        ("description", "description", "descriptionEn"),
    ),
    # Les noms de produits ne sont PAS traduits : l'appariement repose sur les
    # embeddings multilingues, pas sur le nom français, et la correction de
    # @POST /apparier_ingredient juge la nature des produits « à la lecture de
    # leurs noms » (§A.2). Traduire une marque (« Hershey's » → « Sirop de
    # Hershey ») dégraderait justement ce qui est évalué. On conserve donc le nom
    # d'origine tel quel. Cela évite aussi de traduire ~50 000 noms (coût mémoire
    # et temps dominant). Voir §2 : « uniformiser la langue » = langue d'origine.
    PRODUCT: (),
}


def fill_french_fields(kind: str, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Traduit en un seul passage les champs français d'un lot de documents.

    Pour les recettes : le titre et la description (champs scalaires) ainsi que
    le nom de chaque ingrédient. Les noms d'ingrédients sont dédupliqués sur le
    lot avant traduction (ils se répètent beaucoup d'une recette à l'autre), puis
    réécrits. Le nom anglais est conservé et la clé d'appariement ne change pas.
    """
    fields = _TRANSLATABLE_FIELDS.get(kind, ())
    if not fields and kind != RECIPE:
        return documents

    documents = _translate_scalar_fields(documents, fields)
    if kind == RECIPE:
        documents = _translate_ingredients(documents)
    return documents


def _translate_scalar_fields(
    documents: list[dict[str, Any]], fields: tuple[tuple[str, str, str], ...]
) -> list[dict[str, Any]]:
    if not fields:
        return documents
    requests = _collect_requests(documents, fields)
    if not requests:
        return documents
    translations = translate_to_french([text for _, text in requests])
    by_position = _group_by_document(requests, translations)
    return [
        _apply(document, index, fields, by_position)
        for index, document in enumerate(documents)
    ]


def _translate_ingredients(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Traduit le nom des ingrédients, en dédupliquant sur le lot.

    Chaque ingrédient devient ``{nom: <français>, nomEn: <anglais>, cle,
    texteOriginal}``. La clé d'appariement (``cle``) reste inchangée pour ne pas
    perturber l'appariement par embeddings, qui reste la source de vérité de
    @POST /apparier_ingredient.
    """
    unique_names = sorted(
        {
            ingredient["nom"]
            for document in documents
            for ingredient in document.get("ingredients", [])
            if _translatable_name(ingredient)
        }
    )
    if not unique_names:
        return documents

    french_by_name = dict(zip(unique_names, translate_to_french(unique_names)))
    for document in documents:
        ingredients = document.get("ingredients")
        if isinstance(ingredients, list):
            document["ingredients"] = [
                _french_ingredient(ingredient, french_by_name) for ingredient in ingredients
            ]
    return documents


def _translatable_name(ingredient: Any) -> bool:
    return (
        isinstance(ingredient, dict)
        and isinstance(ingredient.get("nom"), str)
        and bool(ingredient["nom"].strip())
    )


def _french_ingredient(
    ingredient: dict[str, Any], french_by_name: dict[str, str]
) -> dict[str, Any]:
    original = ingredient.get("nom")
    french = french_by_name.get(original) if isinstance(original, str) else None
    if french is None:
        return ingredient
    return {**ingredient, "nom": french, "nomEn": original}


def _collect_requests(
    documents: list[dict[str, Any]], fields: tuple[tuple[str, str, str], ...]
) -> list[tuple[int, str]]:
    requests: list[tuple[int, str]] = []
    for index, document in enumerate(documents):
        for source_field, _, _ in fields:
            text = document.get(source_field)
            if isinstance(text, str) and text.strip():
                requests.append((index, text))
    return requests


def _group_by_document(
    requests: list[tuple[int, str]], translations: list[str]
) -> dict[int, dict[str, str]]:
    grouped: dict[int, dict[str, str]] = {}
    for (index, original), translated in zip(requests, translations):
        grouped.setdefault(index, {})[original] = translated
    return grouped


def _apply(
    document: dict[str, Any],
    index: int,
    fields: tuple[tuple[str, str, str], ...],
    by_position: dict[int, dict[str, str]],
) -> dict[str, Any]:
    translated = by_position.get(index)
    if translated is None:
        return document
    result = dict(document)
    for source_field, french_field, english_field in fields:
        original = document.get(source_field)
        if isinstance(original, str) and original in translated:
            result[english_field] = original
            result[french_field] = translated[original]
    return result
