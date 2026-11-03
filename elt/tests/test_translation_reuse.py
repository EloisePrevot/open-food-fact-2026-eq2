from __future__ import annotations

import unittest
from typing import Any

from load.translation_reuse import reuse_translations

RECIPE_ID = "recipe:1"


def english_recipe(**overrides: Any) -> dict[str, Any]:
    recipe = {
        "_id": RECIPE_ID,
        "nom": "Chocolate cake",
        "description": "A rich dessert",
        "ingredients": [{"nom": "sugar", "cle": "sugar", "texteOriginal": "1 cup sugar"}],
    }
    recipe.update(overrides)
    return recipe


def stored_recipe(**overrides: Any) -> dict[str, Any]:
    recipe = {
        "_id": RECIPE_ID,
        "nom": "Gâteau au chocolat",
        "nomEn": "Chocolate cake",
        "description": "Un dessert riche",
        "descriptionEn": "A rich dessert",
        "ingredients": [{"nom": "sucre", "nomEn": "sugar", "cle": "sugar", "texteOriginal": "1 cup sugar"}],
    }
    recipe.update(overrides)
    return recipe


class ReuseTranslationsTests(unittest.TestCase):
    def test_given_unchanged_english_when_reusing_then_previous_french_is_kept(self) -> None:
        [reused], pending = reuse_translations([english_recipe()], {RECIPE_ID: stored_recipe()})

        self.assertEqual(pending, [])
        self.assertEqual(reused["nom"], "Gâteau au chocolat")
        self.assertEqual(reused["nomEn"], "Chocolate cake")
        self.assertEqual(reused["description"], "Un dessert riche")
        self.assertEqual(reused["descriptionEn"], "A rich dessert")
        self.assertEqual(reused["ingredients"][0]["nom"], "sucre")
        self.assertEqual(reused["ingredients"][0]["nomEn"], "sugar")

    def test_given_new_recipe_when_reusing_then_it_is_pending(self) -> None:
        recipe = english_recipe()

        reused, pending = reuse_translations([recipe], {})

        self.assertEqual(reused, [])
        self.assertEqual(pending, [recipe])

    def test_given_changed_title_when_reusing_then_it_is_pending(self) -> None:
        recipe = english_recipe(nom="Vanilla cake")

        reused, pending = reuse_translations([recipe], {RECIPE_ID: stored_recipe()})

        self.assertEqual(reused, [])
        self.assertEqual(pending, [recipe])

    def test_given_changed_ingredient_when_reusing_then_it_is_pending(self) -> None:
        recipe = english_recipe(ingredients=[{"nom": "honey", "cle": "honey", "texteOriginal": "honey"}])

        reused, pending = reuse_translations([recipe], {RECIPE_ID: stored_recipe()})

        self.assertEqual(reused, [])
        self.assertEqual(pending, [recipe])

    def test_given_added_ingredient_when_reusing_then_it_is_pending(self) -> None:
        ingredients = english_recipe()["ingredients"] + [{"nom": "egg", "cle": "egg", "texteOriginal": "1 egg"}]
        recipe = english_recipe(ingredients=ingredients)

        reused, pending = reuse_translations([recipe], {RECIPE_ID: stored_recipe()})

        self.assertEqual(reused, [])
        self.assertEqual(pending, [recipe])

    def test_given_blank_description_when_reusing_then_it_stays_blank(self) -> None:
        stored = stored_recipe(description="")
        del stored["descriptionEn"]

        [reused], _ = reuse_translations([english_recipe(description="")], {RECIPE_ID: stored})

        self.assertEqual(reused["description"], "")
        self.assertNotIn("descriptionEn", reused)

    def test_given_stored_recipe_never_translated_when_reusing_then_it_is_pending(self) -> None:
        stored = stored_recipe(nom="Chocolate cake")
        del stored["nomEn"]

        reused, _ = reuse_translations([english_recipe()], {RECIPE_ID: stored})

        self.assertEqual(reused, [])

    def test_given_reused_ingredient_when_reusing_then_current_key_is_kept(self) -> None:
        recipe = english_recipe(ingredients=[{"nom": "sugar", "cle": "sucre-v2", "texteOriginal": "2 cups sugar"}])

        [reused], _ = reuse_translations([recipe], {RECIPE_ID: stored_recipe()})

        self.assertEqual(reused["ingredients"][0]["cle"], "sucre-v2")
        self.assertEqual(reused["ingredients"][0]["texteOriginal"], "2 cups sugar")


if __name__ == "__main__":
    unittest.main()
