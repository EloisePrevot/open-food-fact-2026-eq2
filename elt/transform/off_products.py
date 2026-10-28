from __future__ import annotations

import sqlite3
from collections import Counter
from collections.abc import Iterator
from typing import Any

from extract.extract import OFF_SOURCE
from transform.ingredient_identity import ingredient_keys
from transform.raw_records import RawRow, clean_rows, iter_raw_rows
from transform.values import grade, optional_text, split_tags, strip_language, text, to_float, to_int

SOURCE = "off"
NORTH_AMERICA_COUNTRIES = ("canada", "united-states", "mexico")
_NUTRIMENT_SUFFIX = "_100g"


def off_product_documents(sqlite: sqlite3.Connection, stats: Counter) -> Iterator[dict[str, Any]]:
    rows = iter_raw_rows(sqlite, OFF_SOURCE, text_filters=NORTH_AMERICA_COUNTRIES)
    return clean_rows(rows, clean_off_product, stats)


def clean_off_product(row: RawRow) -> dict[str, Any] | None:
    raw = row.payload
    code = text(raw.get("code"))
    name = product_name(raw)
    if not code or not name or not is_north_american(raw):
        return None

    generic_name = text(raw.get("generic_name"))
    brands = split_tags(raw.get("brands"))
    categories = split_tags(raw.get("categories_en"))
    identifiant = f"off:{code}"
    return {
        "_id": identifiant,
        "identifiant": identifiant,
        "source": SOURCE,
        "produitDeBase": False,
        "codeBarres": code,
        "nomProduit": name,
        "nomGenerique": generic_name or None,
        "marque": ", ".join(brands) or None,
        "marques": brands,
        "categorie": main_category(raw, categories),
        "categories": categories,
        "nutriScore": grade(raw.get("nutriscore_grade")),
        "nutriScoreValeur": to_int(raw.get("nutriscore_score")),
        "nova": nova_group(raw),
        "ecoScore": grade(raw.get("environmental_score_grade")),
        "ingredientsTexte": optional_text(raw.get("ingredients_text")),
        "allergenes": split_tags(raw.get("allergens_en")),
        "traces": split_tags(raw.get("traces_en")),
        "analyseIngredients": split_tags(raw.get("ingredients_analysis_tags")),
        "quantite": optional_text(raw.get("quantity")),
        "portion": optional_text(raw.get("serving_size")),
        "portionGrammes": to_float(raw.get("serving_quantity")),
        "pays": split_tags(raw.get("countries_tags")),
        "imageUrl": optional_text(raw.get("image_url")),
        "completude": to_float(raw.get("completeness")),
        "nutriments": nutriments_per_100g(raw),
        "nutrimentsBase": "100 g",
        "cles": ingredient_keys(generic_name, name),
        "refBrut": row.reference(),
    }


def is_north_american(raw: dict[str, Any]) -> bool:
    countries = {strip_language(tag.casefold()) for tag in split_tags(raw.get("countries_tags"))}
    return not countries.isdisjoint(NORTH_AMERICA_COUNTRIES)


def product_name(raw: dict[str, Any]) -> str:
    return (
        text(raw.get("product_name"))
        or text(raw.get("generic_name"))
        or text(raw.get("abbreviated_product_name"))
    )


def main_category(raw: dict[str, Any], categories: list[str]) -> str | None:
    pnns_group = optional_text(raw.get("pnns_groups_1"))
    if pnns_group and pnns_group.casefold() == "unknown":
        pnns_group = None
    fallback = categories[0] if categories else None
    return optional_text(raw.get("main_category_en")) or pnns_group or fallback


def nova_group(raw: dict[str, Any]) -> int | None:
    nova = to_int(raw.get("nova_group"))
    return nova if nova in (1, 2, 3, 4) else None


def nutriments_per_100g(raw: dict[str, Any]) -> dict[str, float]:
    nutriments = {}
    for field, value in raw.items():
        number = to_float(value) if field.endswith(_NUTRIMENT_SUFFIX) else None
        if number is not None:
            nutriments[field.removesuffix(_NUTRIMENT_SUFFIX)] = number
    return nutriments
