from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch

from transform.french_fields import PRODUCT, RECIPE, fill_french_fields

ENGLISH_RECIPE_NAME = "Chocolate cake"
ENGLISH_RECIPE_DESCRIPTION = "A rich dessert"
ENGLISH_PRODUCT_NAME = "unbleached all-purpose flour"


def fake_translate(texts: list[str]) -> list[str]:
    """Traducteur déterministe : préfixe 'fr:' pour rendre la traduction visible."""
    return [f"fr:{text}" if text and text.strip() else text for text in texts]


def build_recipe(**overrides: Any) -> dict[str, Any]:
    recipe = {
        "_id": "recipe:1",
        "source": "kaggle",
        "nom": ENGLISH_RECIPE_NAME,
        "description": ENGLISH_RECIPE_DESCRIPTION,
    }
    recipe.update(overrides)
    return recipe


def build_product(**overrides: Any) -> dict[str, Any]:
    product = {"_id": "off:1", "source": "off", "nomProduit": ENGLISH_PRODUCT_NAME}
    product.update(overrides)
    return product


class FillFrenchFieldsTests(unittest.TestCase):
    def setUp(self) -> None:
        patcher = patch("transform.french_fields.translate_to_french", side_effect=fake_translate)
        self.translate = patcher.start()
        self.addCleanup(patcher.stop)

    def test_recipe_name_and_description_are_translated_english_is_kept(self) -> None:
        [recipe] = fill_french_fields(RECIPE, [build_recipe()])

        self.assertEqual(recipe["nom"], f"fr:{ENGLISH_RECIPE_NAME}")
        self.assertEqual(recipe["nomEn"], ENGLISH_RECIPE_NAME)
        self.assertEqual(recipe["description"], f"fr:{ENGLISH_RECIPE_DESCRIPTION}")
        self.assertEqual(recipe["descriptionEn"], ENGLISH_RECIPE_DESCRIPTION)

    def test_product_names_are_not_translated(self) -> None:
        # L'appariement repose sur les embeddings ; les noms de produits restent
        # dans leur langue d'origine (voir french_fields._TRANSLATABLE_FIELDS).
        original = build_product()

        [product] = fill_french_fields(PRODUCT, [original])

        self.assertEqual(product["nomProduit"], ENGLISH_PRODUCT_NAME)
        self.assertNotIn("nomProduitEn", product)
        self.translate.assert_not_called()

    def test_blank_fields_are_not_sent_to_the_translator(self) -> None:
        fill_french_fields(RECIPE, [build_recipe(nom="Soup", description="  ")])

        sent = self.translate.call_args.args[0]
        self.assertEqual(sent, ["Soup"])

    def test_whole_batch_is_translated_in_a_single_call(self) -> None:
        batch = [build_recipe(_id="recipe:1"), build_recipe(_id="recipe:2", nom="Pie")]

        fill_french_fields(RECIPE, batch)

        self.assertEqual(self.translate.call_count, 1)

    def test_nothing_to_translate_skips_the_translator(self) -> None:
        fill_french_fields(RECIPE, [build_recipe(nom="", description="")])

        self.translate.assert_not_called()

    def test_unknown_kind_returns_documents_unchanged(self) -> None:
        documents = [{"_id": "x", "source": "off"}]

        result = fill_french_fields("unknown", documents)

        self.assertIs(result, documents)
        self.translate.assert_not_called()


class TranslationPassthroughTests(unittest.TestCase):
    def test_blank_strings_bypass_the_model(self) -> None:
        from transform import translation

        with patch.object(translation, "_translate_batch") as model:
            result = translation.translate_to_french(["", "   "])

        self.assertEqual(result, ["", "   "])
        model.assert_not_called()

    def test_only_non_blank_strings_reach_the_model_in_order(self) -> None:
        from transform import translation

        with patch.object(translation, "_translate_batch", return_value=["fr:A", "fr:B"]) as model:
            result = translation.translate_to_french(["A", "  ", "B"])

        model.assert_called_once_with(["A", "B"])
        self.assertEqual(result, ["fr:A", "  ", "fr:B"])


if __name__ == "__main__":
    unittest.main()
