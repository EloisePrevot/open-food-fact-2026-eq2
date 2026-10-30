"""Nettoyage des descriptions de produits avant l'indexation.

Trois règles, appliquées au nom indexé; le nom d'origine (``nomProduit``) reste
affiché tel quel et l'enregistrement brut n'est jamais modifié :

1. Allégations : les libellés réglementaires et nutritionnels (« Organic »,
   « Sugar Free », « sans gras »…) décrivent l'emballage, pas l'aliment. Ils sont
   retirés du nom nettoyé et conservés dans ``allegations``.
2. Parenthèses : une dénomination alternative entre parenthèses (« Fromage à la
   crème (Cream Cheese) ») est sortie du nom et gardée dans ``nomsAlternatifs``;
   une précision chiffrée (« (6-9% M.G.) ») est retirée, la valeur vit déjà dans
   les nutriments.
3. Catégories génériques : les catégories racines d'OFF (« Snacks », « Plant-based
   foods ») ne distinguent rien. Elles sont retirées des catégories indexées et une
   catégorie principale générique est remplacée par la plus précise du produit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_NUTRIENTS_EN = r"(?:fat|sodium|salt|sugars?|calories?|carbs?|carbohydrates)"
_NUTRIENTS_FR = r"(?:gras|matières grasses|sodium|sel|sucres?|calories|glucides)"

_CLAIM_PATTERNS = (
    r"(?:certified |usda )?organic",
    r"gluten[- ]free",
    r"non[- ]gmo(?: project verified)?",
    r"gmo[- ]free",
    rf"{_NUTRIENTS_EN}[- ]free",
    rf"zero {_NUTRIENTS_EN}",
    r"no (?:added )?(?:sugars?|salt)(?: added)?",
    r"unsweetened",
    rf"(?:low|reduced|less|lower)[- ]{_NUTRIENTS_EN}",
    r"(?:high|good|excellent) (?:source of )?(?:protein|fib(?:er|re))",
    r"source of (?:protein|fib(?:er|re))",
    r"keto(?: friendly)?",
    r"biologique",
    r"bio",
    r"sans gluten",
    r"sans ogm",
    r"sans gras",
    r"sans (?:sucres?|sel)(?: ajoutés?)?",
    r"non sucrée?s?",
    r"non additionnée? de sucres?",
    rf"(?:faible|réduite?|pauvre) en {_NUTRIENTS_FR}",
    rf"teneur réduite en {_NUTRIENTS_FR}",
    r"(?:source|riche) (?:de |d'|en )(?:fibres|protéines)",
)
_CLAIMS = re.compile(r"(?<!\w)(?:" + "|".join(_CLAIM_PATTERNS) + r")(?!\w)", re.IGNORECASE)
_PARENTHESES = re.compile(r"\(([^()]*)\)")
_HAS_DIGIT = re.compile(r"\d")
_SEPARATOR_RUNS = re.compile(r"\s*([,;/&+-])(?:\s*[,;/&+-])+\s*")
_EDGE_SEPARATORS = re.compile(r"^[\s,;/&+-]+|[\s,;/&+-]+$")
_SPACES = re.compile(r"\s+")
_SPACE_BEFORE_PUNCTUATION = re.compile(r"\s+([,;.])")

# Catégories racines de la taxonomie OFF : elles regroupent des milliers de produits sans les distinguer.
_GENERIC_CATEGORIES = frozenset(
    category.casefold()
    for category in (
        "Foods",
        "Groceries",
        "Plant-based foods and beverages",
        "Plant-based foods",
        "Beverages",
        "Beverages and beverages preparations",
        "Snacks",
        "Sweet snacks",
        "Salty snacks",
        "Meals",
        "Breakfasts",
        "Desserts",
        "Condiments",
        "Dairies",
        "Fermented foods",
        "Fermented milk products",
        "Frozen foods",
        "Canned foods",
        "Cereals and potatoes",
        "Cereals and their products",
        "Fruits and vegetables based foods",
        "Fruits based foods",
        "Vegetables based foods",
        "Meats and their products",
        "Null",
        "Unknown",
    )
)


@dataclass(frozen=True)
class CleanedName:
    name: str
    alternative_names: tuple[str, ...] = field(default=())
    claims: tuple[str, ...] = field(default=())


def clean_name(name: str, *, remove_claims: bool) -> CleanedName:
    """Ne retourne jamais un nom vide : si tout est retiré, le nom d'origine est gardé."""
    claims: list[str] = []
    text = name
    if remove_claims:
        claims = [_normalize_spaces(match) for match in _CLAIMS.findall(text)]
        text = _CLAIMS.sub(" ", text)

    alternative_names = tuple(
        _tidy(content)
        for content in _PARENTHESES.findall(text)
        if _tidy(content) and not _HAS_DIGIT.search(content)
    )
    text = _tidy(_PARENTHESES.sub(" ", text))
    return CleanedName(
        name=text or _normalize_spaces(name),
        alternative_names=alternative_names,
        claims=tuple(dict.fromkeys(claim.casefold() for claim in claims)),
    )


def is_generic_category(category: str) -> bool:
    return category.strip().casefold() in _GENERIC_CATEGORIES


def specific_categories(categories: list[str]) -> list[str]:
    return [category for category in categories if not is_generic_category(category)]


def specific_main_category(main_category: str, categories: list[str]) -> str:
    """Les catégories OFF vont du plus général au plus précis : on garde la dernière précise."""
    if main_category and not is_generic_category(main_category):
        return main_category
    specific = specific_categories(categories)
    return specific[-1] if specific else main_category


def _tidy(text: str) -> str:
    text = _SEPARATOR_RUNS.sub(r"\1 ", _normalize_spaces(text))
    text = _SPACE_BEFORE_PUNCTUATION.sub(r"\1", text)
    return _normalize_spaces(_EDGE_SEPARATORS.sub("", _normalize_spaces(text)))


def _normalize_spaces(text: str) -> str:
    return _SPACES.sub(" ", text).strip()
