"""Nutri-Score d'un aliment de base du Fichier canadien sur les éléments nutritifs (FCEN/CNF).

Le FCEN ne publie pas de Nutri-Score : on le calcule toujours. La catégorie
Nutri-Score est déduite du groupe d'aliments et du premier segment du nom anglais
(« Cheese, brie » → fromage). Le pourcentage de fruits, légumes et légumineuses est
estimé par groupe, comme OFF le fait par catégorie quand la teneur est inconnue.
"""

from __future__ import annotations

from typing import Any

from transform.nutri_score.model import (
    FoodCategory,
    NutriScore,
    NutritionFacts,
    energy_in_kj,
    salt_from_sodium,
)
from transform.nutri_score.rules_2023 import compute_nutri_score
from transform.values import text

_MILLIGRAMS_PER_GRAM = 1000

_DAIRY_AND_EGGS = "1"
_SPICES_AND_HERBS = "2"
_BABY_FOODS = "3"
_FATS_AND_OILS = "4"
_FRUITS = "9"
_PORK = "10"
_VEGETABLES = "11"
_NUTS_AND_SEEDS = "12"
_BEEF = "13"
_BEVERAGES = "14"
_LEGUMES = "16"
_LAMB_VEAL_AND_GAME = "17"

_EXEMPTED_GROUPS = frozenset({_SPICES_AND_HERBS, _BABY_FOODS})
_RED_MEAT_GROUPS = frozenset({_PORK, _BEEF, _LAMB_VEAL_AND_GAME})

_ALCOHOL_PREFIXES = ("alcohol", "vodka cooler", "sangria")
_DAIRY_DRINK_PREFIXES = ("milk", "yogourt beverage", "kefir", "eggnog")
_DAIRY_FAT_PREFIXES = ("butter", "cream")
_CHEESE = "cheese"
_WATER = "water"
_PEANUT = "peanut"
_CHESTNUT = "chestnut"
_POTATO_PREFIXES = ("potato", "sweet potato")
_JUICE = "juice"
_WHOLE_LEGUME_PREFIXES = (
    "beans",
    "refried beans",
    "chickpeas",
    "lentils",
    "peas",
    "black-eyed peas",
    "broadbeans",
    "lupins",
    "moth beans",
    "soybeans",
    "soybean kernels",
)
_NEEDS_PREPARED_MARKERS = ("powder", "concentrate", "dry", "dried")
_PREPARED_MARKERS = ("prepared", "water added", "with ")
_SWEETENER_MARKERS = ("artificial sweetener", "aspartame", "sucralose", "diet", "sugar-free", "sugar free")

_MOSTLY_FRUITS_OR_VEGETABLES_PERCENT = 90
_ONLY_FRUITS_PERCENT = 100
_NO_FRUITS_OR_VEGETABLES_PERCENT = 0


def cnf_nutri_score(group_id: str, english_name: str, nutrients: dict[str, dict[str, Any]]) -> NutriScore | None:
    """``nutrients`` : valeurs pour 100 g indexées par symbole FCEN (``KJ``, ``TSUG``, ``NA``…)."""
    name = english_name.casefold()
    category = cnf_food_category(group_id, name)
    if category is None:
        return None
    return compute_nutri_score(category, _nutrition_facts(category, group_id, name, nutrients))


def cnf_food_category(group_id: str, name: str) -> FoodCategory | None:
    """None : le Nutri-Score ne s'applique pas ou ne peut pas être calculé fidèlement."""
    if group_id in _EXEMPTED_GROUPS or _needs_prepared_values(group_id, name):
        return None
    if group_id == _BEVERAGES:
        return _beverage_category(name)
    if group_id == _DAIRY_AND_EGGS:
        return _dairy_category(name)
    if group_id in (_FATS_AND_OILS, _NUTS_AND_SEEDS):
        return FoodCategory.GENERAL if _CHESTNUT in name else FoodCategory.FAT_OIL_NUTS_SEEDS
    if group_id == _LEGUMES and name.startswith(_PEANUT):
        return FoodCategory.FAT_OIL_NUTS_SEEDS
    if group_id in _RED_MEAT_GROUPS:
        return FoodCategory.RED_MEAT
    return FoodCategory.GENERAL


def _beverage_category(name: str) -> FoodCategory | None:
    if name.startswith(_ALCOHOL_PREFIXES):
        return None
    if _first_segment(name) == _WATER:
        return FoodCategory.WATER
    return FoodCategory.BEVERAGE


def _dairy_category(name: str) -> FoodCategory:
    first_segment = _first_segment(name)
    if first_segment == _CHEESE:
        return FoodCategory.CHEESE
    if first_segment.startswith(_DAIRY_DRINK_PREFIXES):
        return FoodCategory.BEVERAGE
    if first_segment.startswith(_DAIRY_FAT_PREFIXES):
        return FoodCategory.FAT_OIL_NUTS_SEEDS
    return FoodCategory.GENERAL


def _needs_prepared_values(group_id: str, name: str) -> bool:
    """Poudres et concentrés à boire : la valeur « tel que vendu » fausserait la note."""
    is_drink = group_id == _BEVERAGES or (
        group_id == _DAIRY_AND_EGGS and _first_segment(name).startswith(_DAIRY_DRINK_PREFIXES)
    )
    return (
        is_drink
        and any(marker in name for marker in _NEEDS_PREPARED_MARKERS)
        and not any(marker in name for marker in _PREPARED_MARKERS)
    )


def _nutrition_facts(
    category: FoodCategory, group_id: str, name: str, nutrients: dict[str, dict[str, Any]]
) -> NutritionFacts | None:
    sodium_mg = _value(nutrients, "NA")
    sodium_g = None if sodium_mg is None else sodium_mg / _MILLIGRAMS_PER_GRAM
    return NutritionFacts.from_declared(
        category,
        energy_kj=energy_in_kj(_value(nutrients, "KJ"), _value(nutrients, "KCAL")),
        sugars_g=_value(nutrients, "TSUG"),
        saturated_fat_g=_value(nutrients, "TSAT"),
        salt_g=salt_from_sodium(sodium_g),
        proteins_g=_value(nutrients, "PROT"),
        fat_g=_value(nutrients, "FAT"),
        carbohydrates_g=_value(nutrients, "CARB"),
        fiber_g=_value(nutrients, "TDF"),
        fruits_vegetables_legumes_percent=_fruits_vegetables_legumes(group_id, name),
        has_non_nutritive_sweeteners=any(marker in name for marker in _SWEETENER_MARKERS),
    )


def _fruits_vegetables_legumes(group_id: str, name: str) -> float:
    first_segment = _first_segment(name)
    if group_id == _FRUITS:
        return _ONLY_FRUITS_PERCENT if _JUICE in first_segment else _MOSTLY_FRUITS_OR_VEGETABLES_PERCENT
    if group_id == _BEVERAGES and first_segment == _JUICE:
        return _ONLY_FRUITS_PERCENT
    if group_id == _VEGETABLES:
        if first_segment.startswith(_POTATO_PREFIXES):
            return _NO_FRUITS_OR_VEGETABLES_PERCENT
        return _MOSTLY_FRUITS_OR_VEGETABLES_PERCENT
    if group_id == _LEGUMES and first_segment.startswith(_WHOLE_LEGUME_PREFIXES):
        return _MOSTLY_FRUITS_OR_VEGETABLES_PERCENT
    return _NO_FRUITS_OR_VEGETABLES_PERCENT


def _first_segment(name: str) -> str:
    return text(name.split(",", 1)[0])


def _value(nutrients: dict[str, dict[str, Any]], symbol: str) -> float | None:
    entry = nutrients.get(symbol)
    return None if entry is None else entry.get("valeur")
