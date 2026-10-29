"""Échantillonnage stratifié par catégorie.

L'énoncé (§2.1.5) autorise un sous-échantillon mais met en garde contre un
tirage aléatoire : il fait disparaître les produits rares (farine d'amande,
poudre à pâte…) et flatte artificiellement l'appariement. On conserve donc les
catégories que l'appariement doit distinguer.

Stratégie : un tour de rôle (round-robin) par catégorie. On parcourt le flux une
seule fois ; chaque catégorie reçoit un document à tour de rôle jusqu'à atteindre
la cible globale. Les catégories rares sont ainsi représentées avant qu'une
catégorie dominante ne sature l'échantillon, sans jamais charger tout le flux en
mémoire (au plus ``target`` documents retenus).
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from transform.transform import PRODUCT, RECIPE

_UNCLASSIFIED = "__sans_categorie__"

# Plafond de documents mis en tampon par catégorie. Borne la mémoire quand les
# catégories sont nombreuses (produits OFF) tout en laissant assez de matière au
# tour de rôle pour atteindre la cible quand elles sont peu nombreuses (recettes).
_PER_CATEGORY_CAP = 5000


def resolve_limit(kind: str, default_limit: int | None) -> int | None:
    """Résout la cible d'échantillonnage pour un genre de document.

    Les produits et les recettes n'ont pas le même volume utile : on fixe des
    cibles distinctes par variable d'environnement (``ELT_LIMITE_PRODUITS``,
    ``ELT_LIMITE_RECETTES``), avec repli sur la limite globale ``--limit``. Une
    valeur nulle (0) signifie « aucune limite ».
    """
    from os import getenv

    variable = {RECIPE: "ELT_LIMITE_RECETTES", PRODUCT: "ELT_LIMITE_PRODUITS"}.get(kind)
    if variable is None:
        return default_limit
    raw = getenv(variable)
    if raw is None or raw.strip() == "":
        return default_limit
    value = int(raw)
    return value if value > 0 else None


def category_of(kind: str) -> Callable[[dict[str, Any]], str]:
    """Donne la clé de stratification d'un document selon son genre.

    Les produits se stratifient par ``categorie`` (leur catégorie alimentaire),
    les recettes par leur premier ``type`` de la taxonomie française. Les deux
    champs sont ceux que l'appariement et @GET /type doivent distinguer.
    """
    if kind == RECIPE:
        return _recipe_category
    if kind == PRODUCT:
        return _product_category
    return lambda _document: _UNCLASSIFIED


def _product_category(document: dict[str, Any]) -> str:
    category = document.get("categorie")
    return category.casefold() if isinstance(category, str) and category else _UNCLASSIFIED


def _recipe_category(document: dict[str, Any]) -> str:
    types = document.get("type")
    if isinstance(types, list) and types:
        return str(types[0]).casefold()
    return _UNCLASSIFIED


def stratified_sample(
    documents: Iterable[dict[str, Any]],
    target: int | None,
    category_of: Callable[[dict[str, Any]], str],
) -> Iterator[dict[str, Any]]:
    """Sélectionne ``target`` documents en préservant la diversité des catégories.

    À ``target`` nul (aucune limite), le flux est retourné tel quel. Sinon, les
    documents sont regroupés par catégorie puis prélevés en tour de rôle, ce qui
    répartit la cible entre les catégories plutôt que de prendre les premiers
    arrivés.
    """
    if not target:
        yield from documents
        return

    buckets = _fill_buckets(documents, target, category_of)
    yield from _round_robin(buckets, target)


def _fill_buckets(
    documents: Iterable[dict[str, Any]],
    target: int,
    category_of: Callable[[dict[str, Any]], str],
) -> OrderedDict[str, list[dict[str, Any]]]:
    """Regroupe les documents par catégorie, en un seul passage et sans tout
    charger en mémoire.

    Le tour de rôle ne prélève jamais plus de ``target`` documents au total ; il
    est donc inutile d'en garder beaucoup par catégorie. On borne chaque
    catégorie à ``PER_CATEGORY_CAP`` : assez pour alimenter le tour de rôle même
    si peu de catégories existent, mais assez bas pour que la mémoire reste
    bornée quand les catégories sont nombreuses (le cas des produits OFF).
    """
    per_category_cap = max(1, min(target, _PER_CATEGORY_CAP))
    buckets: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for document in documents:
        category = category_of(document) or _UNCLASSIFIED
        bucket = buckets.setdefault(category, [])
        if len(bucket) < per_category_cap:
            bucket.append(document)
    return buckets


def _round_robin(
    buckets: OrderedDict[str, list[dict[str, Any]]], target: int
) -> Iterator[dict[str, Any]]:
    cursors: defaultdict[str, int] = defaultdict(int)
    emitted = 0
    while emitted < target:
        progressed = False
        for category, bucket in buckets.items():
            cursor = cursors[category]
            if cursor < len(bucket):
                yield bucket[cursor]
                cursors[category] = cursor + 1
                emitted += 1
                progressed = True
                if emitted >= target:
                    return
        if not progressed:
            return
