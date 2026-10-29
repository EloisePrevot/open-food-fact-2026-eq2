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
    """Traduit en un seul passage tous les champs d'un lot de documents.

    Les produits de base (CNF) portent déjà un nom français issu de la source :
    on ne les retraduit pas. On ne traduit que ce qui n'a pas d'équivalent
    français, puis on réécrit chaque document avec ses champs remplis.
    """
    fields = _TRANSLATABLE_FIELDS.get(kind, ())
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
