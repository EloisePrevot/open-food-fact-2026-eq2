from __future__ import annotations

import unittest

from transform.recipe_taxonomy import RECIPE_TYPES, french_recipe_types

DEFAULT_TYPE = "Plat principal"


class FrenchRecipeTypesTests(unittest.TestCase):
    def test_single_course_maps_to_its_french_type(self) -> None:
        self.assertEqual(french_recipe_types({"course_list": ["dessert"]}), ["Dessert"])

    def test_courses_are_returned_in_canonical_order(self) -> None:
        result = french_recipe_types({"course_list": ["dessert", "breakfast", "main"]})

        self.assertEqual(result, ["Déjeuner", "Plat principal", "Dessert"])

    def test_course_matching_is_case_insensitive(self) -> None:
        self.assertEqual(french_recipe_types({"course_list": ["DESSERT"]}), ["Dessert"])

    def test_unknown_course_falls_back_to_default(self) -> None:
        self.assertEqual(french_recipe_types({"course_list": ["unknown"]}), [DEFAULT_TYPE])

    def test_missing_course_list_falls_back_to_default(self) -> None:
        self.assertEqual(french_recipe_types({}), [DEFAULT_TYPE])

    def test_duplicate_courses_do_not_duplicate_types(self) -> None:
        self.assertEqual(french_recipe_types({"course_list": ["main", "main"]}), ["Plat principal"])

    def test_every_mapped_type_belongs_to_the_published_set(self) -> None:
        produced = {
            french_recipe_types({"course_list": [course]})[0]
            for course in ("main", "side", "dessert", "bread", "drink", "soup")
        }

        self.assertTrue(produced.issubset(set(RECIPE_TYPES)))


if __name__ == "__main__":
    unittest.main()
