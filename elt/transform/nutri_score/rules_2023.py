"""Algorithme Nutri-Score 2023 de Santé publique France.

Barèmes et règles repris de l'implémentation de référence d'Open Food Facts
(``ProductOpener::Nutriscore``, fonctions suffixées ``_2023``). Chaque barème liste
les seuils : un aliment gagne un point par seuil strictement dépassé.
"""

from __future__ import annotations

from transform.nutri_score.model import ORIGIN_COMPUTED, FoodCategory, NutriScore, NutritionFacts

_ENERGY_KJ = (335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350)
_ENERGY_KJ_BEVERAGES = (30, 90, 150, 210, 240, 270, 300, 330, 360, 390)
_ENERGY_FROM_SATURATED_FAT_KJ = (120, 240, 360, 480, 600, 720, 840, 960, 1080, 1200)
_SUGARS_G = (3.4, 6.8, 10, 14, 17, 20, 24, 27, 31, 34, 37, 41, 44, 48, 51)
_SUGARS_G_BEVERAGES = (0.5, 2, 3.5, 5, 6, 7, 8, 9, 10, 11)
_SATURATED_FAT_G = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
_SATURATED_FAT_RATIO_PERCENT = (10, 16, 22, 28, 34, 40, 46, 52, 58, 64)
_SALT_G = (0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.2, 3.4, 3.6, 3.8, 4)
_NON_NUTRITIVE_SWEETENERS_POINTS = 4

_FRUITS_VEGETABLES_LEGUMES_PERCENT = (40, 60, 80, 80, 80)
_FRUITS_VEGETABLES_LEGUMES_PERCENT_BEVERAGES = (40, 40, 60, 60, 80, 80)
_FIBER_G = (3.0, 4.1, 5.2, 6.3, 7.4)
_PROTEINS_G = (2.4, 4.8, 7.2, 9.6, 12, 14, 17)
_PROTEINS_G_BEVERAGES = (1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0)
_RED_MEAT_MAX_PROTEIN_POINTS = 2

_PROTEINS_COUNTED_BELOW_NEGATIVE_POINTS = 11
_PROTEINS_COUNTED_BELOW_NEGATIVE_POINTS_FATS = 7

# Bornes supérieures inclusives du score pour chaque lettre; au-delà : « e ».
_GRADE_UPPER_BOUNDS = (("a", 0), ("b", 2), ("c", 10), ("d", 18))
_GRADE_UPPER_BOUNDS_FATS = (("a", -6), ("b", 2), ("c", 10), ("d", 18))
_GRADE_UPPER_BOUNDS_BEVERAGES = (("b", 2), ("c", 6), ("d", 9))
_WATER_GRADE = "a"
_WORST_GRADE = "e"


def compute_nutri_score(category: FoodCategory, facts: NutritionFacts | None) -> NutriScore | None:
    """Les eaux sont toujours classées A; sinon il faut toutes les valeurs obligatoires."""
    if category is FoodCategory.WATER:
        score = None if facts is None else _score(category, facts)
        return NutriScore(grade=_WATER_GRADE, score=score, origin=ORIGIN_COMPUTED)
    if facts is None:
        return None
    score = _score(category, facts)
    return NutriScore(grade=_grade(category, score), score=score, origin=ORIGIN_COMPUTED)


def _score(category: FoodCategory, facts: NutritionFacts) -> int:
    negative = _negative_points(category, facts)
    positive = _fiber_points(facts) + _fruits_vegetables_legumes_points(category, facts)
    if _proteins_counted(category, negative):
        positive += _protein_points(category, facts)
    return negative - positive


def _negative_points(category: FoodCategory, facts: NutritionFacts) -> int:
    if category is FoodCategory.FAT_OIL_NUTS_SEEDS:
        energy = _points(facts.energy_from_saturated_fat_kj, _ENERGY_FROM_SATURATED_FAT_KJ)
        saturated_fat = _points(
            facts.saturated_fat_ratio_percent, _SATURATED_FAT_RATIO_PERCENT, inclusive=True
        )
    else:
        energy_thresholds = _ENERGY_KJ_BEVERAGES if category.is_beverage else _ENERGY_KJ
        energy = _points(facts.energy_kj, energy_thresholds)
        saturated_fat = _points(facts.saturated_fat_g, _SATURATED_FAT_G)

    sugars_thresholds = _SUGARS_G_BEVERAGES if category.is_beverage else _SUGARS_G
    sweeteners = (
        _NON_NUTRITIVE_SWEETENERS_POINTS
        if category.is_beverage and facts.has_non_nutritive_sweeteners
        else 0
    )
    return (
        energy
        + _points(facts.sugars_g, sugars_thresholds)
        + saturated_fat
        + _points(facts.salt_g, _SALT_G)
        + sweeteners
    )


def _proteins_counted(category: FoodCategory, negative_points: int) -> bool:
    if category.is_beverage or category is FoodCategory.CHEESE:
        return True
    if category is FoodCategory.FAT_OIL_NUTS_SEEDS:
        return negative_points < _PROTEINS_COUNTED_BELOW_NEGATIVE_POINTS_FATS
    return negative_points < _PROTEINS_COUNTED_BELOW_NEGATIVE_POINTS


def _protein_points(category: FoodCategory, facts: NutritionFacts) -> int:
    thresholds = _PROTEINS_G_BEVERAGES if category.is_beverage else _PROTEINS_G
    points = _points(facts.proteins_g, thresholds)
    if category is FoodCategory.RED_MEAT:
        return min(points, _RED_MEAT_MAX_PROTEIN_POINTS)
    return points


def _fiber_points(facts: NutritionFacts) -> int:
    return _points(facts.fiber_g, _FIBER_G)


def _fruits_vegetables_legumes_points(category: FoodCategory, facts: NutritionFacts) -> int:
    thresholds = (
        _FRUITS_VEGETABLES_LEGUMES_PERCENT_BEVERAGES
        if category.is_beverage
        else _FRUITS_VEGETABLES_LEGUMES_PERCENT
    )
    return _points(facts.fruits_vegetables_legumes_percent, thresholds)


def _grade(category: FoodCategory, score: int) -> str:
    if category.is_beverage:
        bounds = _GRADE_UPPER_BOUNDS_BEVERAGES
    elif category is FoodCategory.FAT_OIL_NUTS_SEEDS:
        bounds = _GRADE_UPPER_BOUNDS_FATS
    else:
        bounds = _GRADE_UPPER_BOUNDS
    return next((grade for grade, upper in bounds if score <= upper), _WORST_GRADE)


def _points(value: float, thresholds: tuple[float, ...], *, inclusive: bool = False) -> int:
    if inclusive:
        return sum(1 for threshold in thresholds if value >= threshold)
    return sum(1 for threshold in thresholds if value > threshold)
