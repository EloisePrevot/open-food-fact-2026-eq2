from __future__ import annotations

import psycopg
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from extract.extract import CNF_SOURCE, KAGGLE_SOURCE, OFF_SOURCE
from transform import cnf_foods, off_products, recipes
from transform.qdrant_points import product_point, recipe_point

RECIPE = "recipe"
PRODUCT = "product"

Documents = Callable[[psycopg.Connection, Counter], Iterator[dict[str, Any]]]


@dataclass(frozen=True)
class DocumentSource:
    label: str
    source: str
    raw_source: str
    kind: str
    documents: Documents
    to_point: Callable[[dict[str, Any]], dict[str, Any]]


DOCUMENT_SOURCES = (
    DocumentSource("recettes", recipes.SOURCE, KAGGLE_SOURCE, RECIPE, recipes.recipe_documents, recipe_point),
    DocumentSource(
        "aliments CNF", cnf_foods.SOURCE, CNF_SOURCE, PRODUCT, cnf_foods.cnf_food_documents, product_point
    ),
    DocumentSource(
        "produits OFF", off_products.SOURCE, OFF_SOURCE, PRODUCT, off_products.off_product_documents, product_point
    ),
)
