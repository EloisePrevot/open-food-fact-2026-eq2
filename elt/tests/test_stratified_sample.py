from __future__ import annotations

import unittest
from collections import Counter
from unittest.mock import patch

from load.stratified_sample import category_of, resolve_limit, stratified_sample
from transform.transform import PRODUCT, RECIPE


def product(category: str, identifier: str) -> dict:
    return {"identifiant": identifier, "categorie": category}


class StratifiedSampleTests(unittest.TestCase):
    def test_no_limit_returns_every_document(self) -> None:
        documents = [product("a", "1"), product("b", "2")]

        result = list(stratified_sample(documents, 0, category_of(PRODUCT)))

        self.assertEqual(result, documents)

    def test_rare_category_survives_against_a_dominant_one(self) -> None:
        dominant = [product("common", str(index)) for index in range(100)]
        rare = [product("rare", "rare-1")]

        result = list(stratified_sample(dominant + rare, 10, category_of(PRODUCT)))

        categories = {document["categorie"] for document in result}
        self.assertIn("rare", categories)

    def test_respects_the_target_count(self) -> None:
        documents = [product(f"cat{index % 5}", str(index)) for index in range(100)]

        result = list(stratified_sample(documents, 12, category_of(PRODUCT)))

        self.assertEqual(len(result), 12)

    def test_spreads_the_target_across_categories_round_robin(self) -> None:
        documents = [product(f"cat{index % 4}", str(index)) for index in range(40)]

        result = list(stratified_sample(documents, 8, category_of(PRODUCT)))

        per_category = Counter(document["categorie"] for document in result)
        self.assertEqual(set(per_category.values()), {2})

    def test_per_category_buffer_is_bounded(self) -> None:
        from load.stratified_sample import _PER_CATEGORY_CAP, _fill_buckets

        documents = [product("same", str(index)) for index in range(_PER_CATEGORY_CAP + 500)]

        buckets = _fill_buckets(iter(documents), _PER_CATEGORY_CAP + 500, category_of(PRODUCT))

        self.assertEqual(len(buckets["same"]), _PER_CATEGORY_CAP)

    def test_returns_all_when_target_exceeds_available(self) -> None:
        documents = [product("a", "1"), product("b", "2")]

        result = list(stratified_sample(documents, 50, category_of(PRODUCT)))

        self.assertEqual(len(result), 2)

    def test_recipe_category_uses_first_type(self) -> None:
        recipes = [
            {"identifiant": "r1", "type": ["Dessert"]},
            {"identifiant": "r2", "type": ["Plat principal"]},
            {"identifiant": "r3", "type": ["Dessert"]},
        ]

        result = list(stratified_sample(recipes, 2, category_of(RECIPE)))

        types = {document["type"][0] for document in result}
        self.assertEqual(types, {"Dessert", "Plat principal"})


class ResolveLimitTests(unittest.TestCase):
    """Les variables d'environnement sont isolées par ``patch.dict`` pour ne pas
    fuir d'un test à l'autre (``clear=False`` conserve le reste de l'environnement)."""

    def test_falls_back_to_default_when_variable_absent(self) -> None:
        with patch.dict("os.environ", {}, clear=False):
            _remove_limit_variables()

            self.assertEqual(resolve_limit(PRODUCT, 5000), 5000)

    def test_reads_product_specific_variable(self) -> None:
        with patch.dict("os.environ", {"ELT_LIMITE_PRODUITS": "50000"}):
            self.assertEqual(resolve_limit(PRODUCT, 5000), 50000)

    def test_zero_means_no_limit(self) -> None:
        with patch.dict("os.environ", {"ELT_LIMITE_RECETTES": "0"}):
            self.assertIsNone(resolve_limit(RECIPE, 5000))


def _remove_limit_variables() -> None:
    import os

    for variable in ("ELT_LIMITE_PRODUITS", "ELT_LIMITE_RECETTES"):
        os.environ.pop(variable, None)


if __name__ == "__main__":
    unittest.main()
