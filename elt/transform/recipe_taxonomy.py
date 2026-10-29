"""Taxonomie française des recettes.

L'énoncé recommande « un moyen de catégoriser moins complexe que celui
actuellement utilisé » (§2). La source Kaggle porte environ 250 catégories
anglaises brutes (« Air Fryer Recipes », « Chicken Cacciatore »…), trop fines et
en anglais. On s'appuie plutôt sur ``course_list``, un vocabulaire déjà normalisé
d'une dizaine de valeurs, que l'on projette sur un petit ensemble de types
français stables servis par @GET /type.

Traduire les 250 catégories une à une donnerait un français incohérent et des
types qui ne correspondraient pas au corpus. Une taxonomie contrôlée est à la
fois plus simple, reproductible et conforme à l'intention de l'énoncé.
"""

from __future__ import annotations

from transform.values import text_list

# Projection d'une valeur ``course_list`` (normalisée par la source) vers un type français.
_COURSE_TO_TYPE: dict[str, str] = {
    "main": "Plat principal",
    "side": "Accompagnement",
    "dessert": "Dessert",
    "bread": "Pain",
    "drink": "Boisson",
    "soup": "Soupe",
    "breakfast": "Déjeuner",
    "snack": "Collation",
    "sauce": "Sauce",
    "appetizer": "Entrée",
}

# Type attribué quand aucune valeur exploitable n'est présente : une recette sans
# type ne serait pas trouvable par @GET /type ni filtrable par @POST /recette.
_DEFAULT_TYPE = "Plat principal"

# Tous les types que l'application reconnaît, dans un ordre stable.
RECIPE_TYPES: tuple[str, ...] = (
    "Déjeuner",
    "Entrée",
    "Plat principal",
    "Accompagnement",
    "Soupe",
    "Dessert",
    "Collation",
    "Boisson",
    "Pain",
    "Sauce",
)


def french_recipe_types(raw: dict) -> list[str]:
    """Dérive les types français d'une recette à partir de ``course_list``.

    Les valeurs sont dédupliquées tout en conservant l'ordre canonique défini par
    ``RECIPE_TYPES`` : deux recettes du même ensemble de plats portent exactement
    la même liste, ce qui rend les types comparables.
    """
    courses = {course.casefold() for course in text_list(raw.get("course_list"))}
    matched = [
        french for course, french in _COURSE_TO_TYPE.items() if course in courses
    ]
    ordered = [recipe_type for recipe_type in RECIPE_TYPES if recipe_type in matched]
    return ordered or [_DEFAULT_TYPE]
