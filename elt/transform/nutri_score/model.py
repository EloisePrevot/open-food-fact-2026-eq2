"""Modèle du Nutri-Score : catégorie d'aliment, valeurs nutritives pour 100 g et résultat."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

KJ_PER_KCAL = 4.184
SALT_PER_SODIUM = 2.5
KJ_PER_GRAM_OF_SATURATED_FAT = 37
MAX_PLAUSIBLE_ENERGY_KJ = 3900
MAX_PLAUSIBLE_GRAMS = 100

ORIGIN_SOURCE = "source"
ORIGIN_COMPUTED = "calcule"


class FoodCategory(Enum):
    GENERAL = "general"
    CHEESE = "fromage"
    RED_MEAT = "viande_rouge"
    FAT_OIL_NUTS_SEEDS = "matiere_grasse_noix_graines"
    BEVERAGE = "boisson"
    WATER = "eau"

    @property
    def is_beverage(self) -> bool:
        return self in (FoodCategory.BEVERAGE, FoodCategory.WATER)


@dataclass(frozen=True)
class NutriScore:
    grade: str
    score: int | None
    origin: str


@dataclass(frozen=True)
class NutritionFacts:
    """Valeurs déclarées pour 100 g (ou 100 ml pour les boissons)."""

    energy_kj: float
    sugars_g: float
    saturated_fat_g: float
    salt_g: float
    proteins_g: float
    fat_g: float | None = None
    fiber_g: float = 0.0
    fruits_vegetables_legumes_percent: float = 0.0
    has_non_nutritive_sweeteners: bool = False

    @classmethod
    def from_declared(
        cls,
        category: FoodCategory,
        *,
        energy_kj: float | None,
        sugars_g: float | None,
        saturated_fat_g: float | None,
        salt_g: float | None,
        proteins_g: float | None,
        fat_g: float | None = None,
        carbohydrates_g: float | None = None,
        fiber_g: float | None = None,
        fruits_vegetables_legumes_percent: float | None = None,
        has_non_nutritive_sweeteners: bool = False,
    ) -> NutritionFacts | None:
        """Retourne None si une valeur obligatoire manque ou est invraisemblable.

        Comme Open Food Facts : les sucres valent 0 quand les glucides valent 0, les
        gras saturés valent 0 quand les lipides valent 0, et les fibres absentes
        comptent pour 0. Les lipides ne sont exigés que pour les matières grasses,
        noix et graines (ratio gras saturés / lipides).
        """
        if sugars_g is None and carbohydrates_g == 0:
            sugars_g = 0.0
        if saturated_fat_g is None and fat_g == 0:
            saturated_fat_g = 0.0

        required_grams = (sugars_g, saturated_fat_g, salt_g, proteins_g)
        if energy_kj is None or any(value is None for value in required_grams):
            return None
        if category is FoodCategory.FAT_OIL_NUTS_SEEDS and fat_g is None:
            return None

        optional_grams = (fat_g, fiber_g)
        grams = [value for value in (*required_grams, *optional_grams) if value is not None]
        if not _plausible(energy_kj, grams):
            return None

        return cls(
            energy_kj=energy_kj,
            sugars_g=sugars_g,
            saturated_fat_g=saturated_fat_g,
            salt_g=salt_g,
            proteins_g=proteins_g,
            fat_g=fat_g,
            fiber_g=fiber_g or 0.0,
            fruits_vegetables_legumes_percent=fruits_vegetables_legumes_percent or 0.0,
            has_non_nutritive_sweeteners=has_non_nutritive_sweeteners,
        )

    @property
    def energy_from_saturated_fat_kj(self) -> float:
        return self.saturated_fat_g * KJ_PER_GRAM_OF_SATURATED_FAT

    @property
    def saturated_fat_ratio_percent(self) -> float:
        if self.saturated_fat_g <= 0:
            return 0.0
        fat = self.fat_g if self.fat_g and self.fat_g > 0 else self.saturated_fat_g
        return self.saturated_fat_g / fat * 100


def energy_in_kj(kilojoules: float | None, kilocalories: float | None) -> float | None:
    """Le barème est en kJ; beaucoup de produits nord-américains n'affichent que des kcal."""
    if kilojoules is not None:
        return kilojoules
    return None if kilocalories is None else kilocalories * KJ_PER_KCAL


def salt_from_sodium(sodium_g: float | None) -> float | None:
    return None if sodium_g is None else sodium_g * SALT_PER_SODIUM


def _plausible(energy_kj: float, grams: list[float]) -> bool:
    return 0 <= energy_kj <= MAX_PLAUSIBLE_ENERGY_KJ and all(
        0 <= value <= MAX_PLAUSIBLE_GRAMS for value in grams
    )
