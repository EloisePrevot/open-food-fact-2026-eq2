from __future__ import annotations

import json
import sqlite3
import unittest
from collections import Counter
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

from extract.extract import CNF_SOURCE, KAGGLE_SOURCE, OFF_SOURCE
from load.load_state import LoadState
from load.qdrant_storage import QdrantDataStore, run_qdrant_loads
from raw_models import RawArtifact, RawRecord
from raw_storage import RawDataStore
from transform.cnf_foods import cnf_food_documents
from transform.ingredient_identity import ingredient_key
from transform.off_products import clean_off_product, off_product_documents
from transform.qdrant_points import product_point, recipe_point
from transform.raw_records import RawRow
from transform.recipes import clean_recipe, recipe_documents
from transform.transform import PRODUCT, RECIPE

RECIPE_RAW = {
    "recipe_title": "Poulet simple",
    "category": "Dinner",
    "description": "Un souper rapide",
    "ingredients": ["500 g chicken breast", "salt"],
    "ingredients_canonical": ["chicken breast", "salt"],
    "directions": ["Cook the chicken.", "Season to taste."],
    "course_list": '["main"]',
    "is_vegan": "False",
}

OFF_RAW = {
    "code": "001234",
    "product_name": "Poulet bio",
    "generic_name": "Poitrine de poulet",
    "brands": "Marque A, Marque B",
    "categories_en": "Meats, Chicken",
    "countries_tags": "en:canada",
    "nutriscore_grade": "b",
    "nova_group": "2",
    "proteins_100g": "23.5",
    "fat_100g": "",
}

WINDOWS_PATH = r"cnf-fcen-csv\FOOD NAME.csv"


class FixedEmbedding:
    @staticmethod
    def embed(texts):
        for _ in texts:
            yield np.ones(384, dtype=np.float32)


def raw_database(records: dict[tuple[str, str], list[dict]]) -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    RawDataStore(connection).initialize_schema()
    for (source, path), payloads in records.items():
        cursor = connection.execute(
            "INSERT INTO raw_artifacts (source, relative_path, media_type, encoding, sha256, imported_at)"
            " VALUES (?, ?, 'text/csv', 'utf-8', ?, 'now')",
            (source, path, path),
        )
        connection.executemany(
            "INSERT INTO raw_records VALUES (?, ?, ?, '')",
            [(cursor.lastrowid, ordinal, json.dumps(payload)) for ordinal, payload in enumerate(payloads, 1)],
        )
    return connection


def row(payload: dict) -> RawRow:
    return RawRow(artifact_id=1, ordinal=7, payload=payload)


class RecipeTests(unittest.TestCase):
    def test_ingredient_key_normalizes_accents_and_ligatures(self) -> None:
        self.assertEqual(ingredient_key("Œufs frais"), "oeufs-frais")

    def test_recipe_is_cleaned_with_stable_identity(self) -> None:
        first = clean_recipe(row(RECIPE_RAW))

        self.assertEqual(first["_id"], clean_recipe(row(RECIPE_RAW))["_id"])
        self.assertEqual(first["type"], ["main"])
        self.assertEqual(first["nbIngredients"], 2)
        self.assertEqual(
            first["ingredients"][0],
            {"nom": "chicken breast", "cle": "chicken-breast", "texteOriginal": "500 g chicken breast"},
        )
        self.assertIs(first["regime"]["vegan"], False)
        self.assertEqual(first["refBrut"], {"artifactId": 1, "ordinal": 7})

    def test_duplicate_recipes_keep_first_occurrence(self) -> None:
        sqlite = raw_database(
            {
                (KAGGLE_SOURCE, "kaggle-recipes/recipes_extended.json"): [
                    RECIPE_RAW,
                    {**RECIPE_RAW, "description": "Autre description"},
                ]
            }
        )
        stats: Counter = Counter()

        with closing(sqlite):
            documents = list(recipe_documents(sqlite, stats))

        self.assertEqual([document["description"] for document in documents], ["Un souper rapide"])
        self.assertEqual(stats["doublons"], 1)

    def test_recipe_without_ingredients_is_rejected(self) -> None:
        self.assertIsNone(clean_recipe(row({"recipe_title": "Vide"})))

    def test_recipe_point_keeps_only_identifier_and_type(self) -> None:
        point = recipe_point(clean_recipe(row(RECIPE_RAW)))

        self.assertEqual(set(point["payload"]), {"identifiant", "type"})
        self.assertIn("Poulet simple", point["text"])
        self.assertIn("chicken breast", point["text"])


class OffProductTests(unittest.TestCase):
    def test_north_american_product_is_cleaned(self) -> None:
        product = clean_off_product(row(OFF_RAW))

        self.assertEqual(product["_id"], "off:001234")
        self.assertIs(product["produitDeBase"], False)
        self.assertEqual(product["marques"], ["Marque A", "Marque B"])
        self.assertEqual(product["nutriScore"], "b")
        self.assertEqual(product["nova"], 2)
        self.assertEqual(product["nutriments"], {"proteins": 23.5})
        self.assertEqual(product["cles"], ["poitrine-de-poulet", "poulet-bio"])

    def test_product_outside_north_america_is_rejected(self) -> None:
        self.assertIsNone(clean_off_product(row({**OFF_RAW, "countries_tags": "en:france"})))

    def test_unknown_quality_values_are_not_fabricated(self) -> None:
        product = clean_off_product(row({**OFF_RAW, "nutriscore_grade": "unknown", "nova_group": "x"}))

        self.assertIsNone(product["nutriScore"])
        self.assertIsNone(product["nova"])

    def test_product_point_keeps_only_filter_fields(self) -> None:
        point = product_point(clean_off_product(row(OFF_RAW)))

        self.assertEqual(
            point["payload"],
            {
                "identifiant": "off:001234",
                "produitDeBase": False,
                "marques": ["marque a", "marque b"],
                "nutriScore": "b",
                "nova": 2,
            },
        )

    def test_documents_are_read_from_sqlite_and_filtered(self) -> None:
        sqlite = raw_database(
            {(OFF_SOURCE, "off.csv"): [OFF_RAW, {**OFF_RAW, "code": "9", "countries_tags": "en:france"}]}
        )
        with closing(sqlite):
            documents = list(off_product_documents(sqlite, Counter()))

        self.assertEqual([document["_id"] for document in documents], ["off:001234"])


class CnfFoodTests(unittest.TestCase):
    def test_food_is_joined_with_group_and_nutrients(self) -> None:
        sqlite = raw_database(
            {
                (CNF_SOURCE, "cnf/FOOD GROUP.csv"): [
                    {"FoodGroupID": "11", "FoodGroupName": "Vegetables", "FoodGroupNameF": "Légumes"}
                ],
                (CNF_SOURCE, "cnf/NUTRIENT NAME.csv"): [
                    {"NutrientID": "203", "NutrientCode": "203", "NutrientSymbol": "PROT",
                     "NutrientName": "PROTEIN", "NutrientNameF": "PROTÉINES", "NutrientUnit": "g"}
                ],
                (CNF_SOURCE, "cnf/NUTRIENT AMOUNT.csv"): [
                    {"FoodID": "42", "NutrientID": "203", "NutrientValue": "0.93", "StandardError": ""}
                ],
                (CNF_SOURCE, "cnf/FOOD NAME.csv"): [
                    {"FoodID": "42", "FoodGroupID": "11", "FoodDescription": "Carrots, raw",
                     "FoodDescriptionF": "Carottes crues"}
                ],
            }
        )

        with closing(sqlite):
            [food] = list(cnf_food_documents(sqlite, Counter()))

        self.assertEqual(food["_id"], "cnf:42")
        self.assertIs(food["produitDeBase"], True)
        self.assertEqual(food["categorie"], "Légumes")
        self.assertEqual(food["nutriments"]["PROT"]["valeur"], 0.93)
        self.assertNotIn("erreurType", food["nutriments"]["PROT"])
        self.assertEqual(food["cles"], ["carottes-crues", "carrots-raw"])


class QdrantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = QdrantClient(":memory:")
        self.store = QdrantDataStore(self.client, FixedEmbedding())
        self.store.ensure_collections()

    def tearDown(self) -> None:
        self.client.close()

    def test_product_search_applies_filters(self) -> None:
        preferred = product_point(clean_off_product(row(OFF_RAW)))
        filtered = product_point(
            clean_off_product(row({**OFF_RAW, "code": "2", "brands": "Autre", "nutriscore_grade": "d", "nova_group": "4"}))
        )
        self.store.upsert(PRODUCT, [preferred, filtered])

        result = self.store.search_products(
            "poulet", basic_food=False, brand="Marque A", nutri_score_min="B", nova_max=2
        )

        self.assertEqual([point.payload["identifiant"] for point in result.points], ["off:001234"])

    def test_recipe_search_filters_by_type(self) -> None:
        self.store.upsert(RECIPE, [recipe_point(clean_recipe(row(RECIPE_RAW)))])

        self.assertEqual(len(self.store.search_recipes("souper", recipe_type="main").points), 1)
        self.assertEqual(len(self.store.search_recipes("souper", recipe_type="dessert").points), 0)

    def test_qdrant_is_fed_from_sqlite(self) -> None:
        sqlite = raw_database(
            {
                (KAGGLE_SOURCE, "kaggle-recipes/recipes_extended.json"): [RECIPE_RAW],
                (OFF_SOURCE, "off.csv"): [OFF_RAW],
            }
        )
        connections = SimpleNamespace(sqlite=sqlite, qdrant=self.client)

        with closing(sqlite), patch("load.qdrant_storage.TextEmbedding", return_value=FixedEmbedding()):
            summary = run_qdrant_loads(connections, limit=None)

        self.assertEqual(summary["recettes"]["vectorises"], 1)
        self.assertEqual(summary["produits OFF"]["vectorises"], 1)
        self.assertEqual(summary["aliments CNF"]["vectorises"], 0)

    def test_full_load_purges_points_not_reloaded(self) -> None:
        self.add_stale_recipe_point()

        summary = self.load_recipes(limit=None)

        self.assertEqual(summary["supprimes"], {"recipes": 1, "ingredients": 0})
        self.assertEqual(self.client.count("recipes").count, 1)

    def test_limited_load_keeps_points_not_reloaded(self) -> None:
        self.add_stale_recipe_point()

        summary = self.load_recipes(limit=10)

        self.assertNotIn("supprimes", summary)
        self.assertEqual(self.client.count("recipes").count, 2)

    def test_reload_does_not_embed_unchanged_text_again(self) -> None:
        point = recipe_point(clean_recipe(row(RECIPE_RAW)))
        self.store.upsert(RECIPE, [point])

        stats = self.store.upsert(RECIPE, [point])

        self.assertEqual(stats, {"vectorises": 0, "inchanges": 1})

    def test_reload_refreshes_payload_without_embedding(self) -> None:
        point = recipe_point(clean_recipe(row(RECIPE_RAW)))
        self.store.upsert(RECIPE, [point])
        retyped = {**point, "payload": {**point["payload"], "type": ["dessert"]}}

        stats = self.store.upsert(RECIPE, [retyped])

        self.assertEqual(stats["vectorises"], 0)
        self.assertEqual(len(self.store.search_recipes("souper", recipe_type="dessert").points), 1)

    def test_reload_embeds_changed_text(self) -> None:
        point = recipe_point(clean_recipe(row(RECIPE_RAW)))
        self.store.upsert(RECIPE, [point])

        stats = self.store.upsert(RECIPE, [{**point, "text": point["text"] + " épicé"}])

        self.assertEqual(stats["vectorises"], 1)

    def test_up_to_date_source_is_skipped_and_not_purged(self) -> None:
        self.load_recipes(limit=None)

        summary = self.load_recipes(limit=None, skip_up_to_date=True)

        self.assertEqual(summary["recettes"], {"dejaAJour": 1})
        self.assertEqual(summary["supprimes"], {})
        self.assertEqual(self.client.count("recipes").count, 1)

    def test_source_loaded_with_a_limit_is_reloaded_without_limit(self) -> None:
        self.load_recipes(limit=10)

        summary = self.load_recipes(limit=None, skip_up_to_date=True)

        self.assertEqual(summary["recettes"]["inchanges"], 1)

    def add_stale_recipe_point(self) -> None:
        self.client.upsert(
            "recipes",
            [models.PointStruct(id=str(uuid4()), vector=[1.0] * 384, payload={"recipe_id": "ancien"})],
        )

    def load_recipes(self, limit: int | None, skip_up_to_date: bool = False) -> dict:
        sqlite = raw_database({(KAGGLE_SOURCE, "kaggle-recipes/recipes_extended.json"): [RECIPE_RAW]})
        connections = SimpleNamespace(sqlite=sqlite, qdrant=self.client)
        with closing(sqlite), patch("load.qdrant_storage.TextEmbedding", return_value=FixedEmbedding()):
            return run_qdrant_loads(connections, limit=limit, skip_up_to_date=skip_up_to_date)


class LoadStateTests(unittest.TestCase):
    def test_full_load_covers_any_limit(self) -> None:
        self.assertTrue(LoadState("v1", None).covers(LoadState("v1", 500)))

    def test_limited_load_does_not_cover_a_larger_load(self) -> None:
        self.assertFalse(LoadState("v1", 500).covers(LoadState("v1", None)))
        self.assertFalse(LoadState("v1", 500).covers(LoadState("v1", 1000)))

    def test_other_version_is_not_covered(self) -> None:
        self.assertFalse(LoadState("v1", None).covers(LoadState("v2", None)))


class RawDataStoreTests(unittest.TestCase):
    def test_windows_paths_are_normalized(self) -> None:
        with closing(raw_database({(CNF_SOURCE, WINDOWS_PATH): []})) as sqlite:
            RawDataStore(sqlite).initialize_schema()

            paths = [path for (path,) in sqlite.execute("SELECT relative_path FROM raw_artifacts")]

        self.assertEqual(paths, ["cnf-fcen-csv/FOOD NAME.csv"])

    def test_same_file_is_not_ingested_twice(self) -> None:
        with TemporaryDirectory() as directory, closing(sqlite3.connect(":memory:")) as sqlite:
            artifact = self.artifact(Path(directory))
            store = RawDataStore(sqlite)
            store.initialize_schema()
            store.ingest(artifact, [RawRecord(1, {"a": 1})])

            self.assertIsNone(store.ingest(artifact, [RawRecord(1, {"a": 1})]))

    @staticmethod
    def artifact(directory: Path) -> RawArtifact:
        path = directory / "off.csv"
        path.write_text("a,b", encoding="utf-8")
        return RawArtifact(OFF_SOURCE, path, "off.csv", "utf-8", "text/csv")


if __name__ == "__main__":
    unittest.main()
