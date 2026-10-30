"""Nutri-Score d'un produit Open Food Facts.

On garde la note publiée par OFF quand elle existe. Sinon on la calcule à partir
des valeurs pour 100 g. Écart volontaire avec OFF : un produit sans catégorie est
traité comme un aliment général au lieu d'être laissé sans note; c'est la cause
principale des notes manquantes sur les produits nord-américains.
Listes de catégories reprises de ``ProductOpener::Food`` et ``Config_off.pm``.
"""

from __future__ import annotations

from typing import Any

from transform.nutri_score.model import (
    ORIGIN_SOURCE,
    FoodCategory,
    NutriScore,
    NutritionFacts,
    energy_in_kj,
    salt_from_sodium,
)
from transform.nutri_score.rules_2023 import compute_nutri_score
from transform.values import grade, split_tags, text, to_int

_NOT_APPLICABLE_GRADE = "not-applicable"

_EXEMPTED = frozenset(
    {
        "en:alcoholic-beverages",
        "en:baby-foods",
        "en:baby-milks",
        "en:chewing-gum",
        "en:food-additives",
        "en:dietary-supplements",
        "en:meal-replacements",
        "en:salts",
        "en:spices",
        "en:sugar-substitutes",
        "en:vinegars",
        "en:non-food-products",
    }
)
_NOT_EXEMPTED = frozenset(
    {
        "en:tea-based-beverages",
        "en:iced-teas",
        "en:herbal-tea-beverages",
        "en:coffee-beverages",
        "en:coffee-drinks",
    }
)
# Les valeurs « telles que vendues » ne conviennent pas : il faudrait celles du produit préparé.
_NEEDS_PREPARED_VALUES = frozenset(
    {
        "en:dried-products-to-be-rehydrated",
        "en:cocoa-and-chocolate-powders",
        "en:dessert-mixes",
        "en:flavoured-syrups",
        "en:instant-beverages",
        "en:beverage-preparations",
    }
)

_BEVERAGES = frozenset({"en:beverages", "en:beverage-preparations"})
_NOT_BEVERAGES = frozenset({"en:meal-replacement", "en:soups"})
_ALWAYS_BEVERAGES = frozenset(
    {
        "en:milks",
        "en:plant-based-milk-alternatives",
        "en:dairy-drinks",
        "en:plant-based-beverages",
        "en:tea-based-beverages",
        "en:iced-teas",
        "en:herbal-tea-beverages",
        "en:coffee-beverages",
        "en:coffee-drinks",
        "en:coffees",
        "en:herbal-teas",
        "en:teas",
    }
)
_WATERS = "en:spring-waters"
_FLAVOURED_WATERS = frozenset({"en:flavored-waters", "en:flavoured-waters"})
_CHEESES = "en:cheeses"
_NOT_CHEESES = "fr:fromages-blancs"
_CHESTNUTS = "en:chestnuts"
# OFF passe par les codes SH du taxonomy pour les noix; on s'en approche par les catégories.
_FATS_OILS_NUTS_SEEDS = frozenset(
    {"en:fats", "en:creams", "en:seeds", "en:nuts", "en:peanuts", "en:peanut-butters", "en:nut-butters"}
)
_RED_MEATS = frozenset(
    {"en:beef", "en:beef-and-its-products", "en:pork", "en:pork-and-its-products", "en:veal", "en:lamb-meat"}
)

# Estimation par catégorie quand la teneur n'est pas déclarée; la première correspondance gagne.
_FRUITS_VEGETABLES_LEGUMES_BY_CATEGORY = (
    ("en:potatoes", 0),
    ("en:sweet-potatoes", 0),
    ("en:fruit-juices", 100),
    ("en:vegetable-juices", 100),
    ("en:fruit-sauces", 90),
    ("en:vegetables", 90),
    ("en:fruits", 90),
    ("en:mushrooms", 90),
    ("en:canned-fruits", 90),
    ("en:frozen-fruits", 90),
    ("en:jams", 50),
)

_NON_NUTRITIVE_SWEETENERS = (
    "en:e950",
    "en:e951",
    "en:e952",
    "en:e954",
    "en:e955",
    "en:e957",
    "en:e959",
    "en:e960",
    "en:e961",
    "en:e962",
    "en:e969",
)


def off_nutri_score(raw: dict[str, Any], nutriments: dict[str, float]) -> NutriScore | None:
    """``nutriments`` : valeurs pour 100 g, clés OFF sans le suffixe ``_100g``."""
    declared_grade = grade(raw.get("nutriscore_grade"))
    if declared_grade:
        return NutriScore(declared_grade, to_int(raw.get("nutriscore_score")), ORIGIN_SOURCE)
    if text(raw.get("nutriscore_grade")).casefold() == _NOT_APPLICABLE_GRADE:
        return None

    categories = frozenset(split_tags(raw.get("categories_tags")))
    category = off_food_category(categories)
    if category is None:
        return None
    return compute_nutri_score(category, _nutrition_facts(category, categories, raw, nutriments))


def off_food_category(categories: frozenset[str]) -> FoodCategory | None:
    """None : le Nutri-Score ne s'applique pas ou ne peut pas être calculé fidèlement."""
    if _is_exempted(categories) or categories & _NEEDS_PREPARED_VALUES:
        return None
    if _WATERS in categories and not categories & _FLAVOURED_WATERS:
        return FoodCategory.WATER
    if _is_beverage(categories):
        return FoodCategory.BEVERAGE
    if _CHEESES in categories and _NOT_CHEESES not in categories:
        return FoodCategory.CHEESE
    if categories & _FATS_OILS_NUTS_SEEDS and _CHESTNUTS not in categories:
        return FoodCategory.FAT_OIL_NUTS_SEEDS
    if categories & _RED_MEATS:
        return FoodCategory.RED_MEAT
    return FoodCategory.GENERAL


def _is_exempted(categories: frozenset[str]) -> bool:
    return bool(categories & _EXEMPTED) and not categories & _NOT_EXEMPTED


def _is_beverage(categories: frozenset[str]) -> bool:
    if categories & _ALWAYS_BEVERAGES:
        return True
    return bool(categories & _BEVERAGES) and not categories & _NOT_BEVERAGES


def _nutrition_facts(
    category: FoodCategory,
    categories: frozenset[str],
    raw: dict[str, Any],
    nutriments: dict[str, float],
) -> NutritionFacts | None:
    salt = nutriments.get("salt")
    return NutritionFacts.from_declared(
        category,
        energy_kj=energy_in_kj(_first(nutriments, "energy-kj", "energy"), nutriments.get("energy-kcal")),
        sugars_g=nutriments.get("sugars"),
        saturated_fat_g=nutriments.get("saturated-fat"),
        salt_g=salt if salt is not None else salt_from_sodium(nutriments.get("sodium")),
        proteins_g=nutriments.get("proteins"),
        fat_g=nutriments.get("fat"),
        carbohydrates_g=nutriments.get("carbohydrates"),
        fiber_g=nutriments.get("fiber"),
        fruits_vegetables_legumes_percent=_fruits_vegetables_legumes(categories, nutriments),
        has_non_nutritive_sweeteners=_has_non_nutritive_sweeteners(raw),
    )


def _fruits_vegetables_legumes(categories: frozenset[str], nutriments: dict[str, float]) -> float | None:
    declared = nutriments.get("fruits-vegetables-legumes")
    if declared is not None:
        return declared
    return next(
        (percent for category, percent in _FRUITS_VEGETABLES_LEGUMES_BY_CATEGORY if category in categories),
        None,
    )


def _has_non_nutritive_sweeteners(raw: dict[str, Any]) -> bool:
    return any(
        additive.startswith(_NON_NUTRITIVE_SWEETENERS) for additive in split_tags(raw.get("additives_tags"))
    )


def _first(nutriments: dict[str, float], *keys: str) -> float | None:
    return next((nutriments[key] for key in keys if key in nutriments), None)
