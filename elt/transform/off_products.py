from __future__ import annotations

import psycopg
from collections import Counter
from collections.abc import Iterator
from typing import Any

from extract.extract import OFF_SOURCE
from transform.description_cleaning import clean_name, specific_categories, specific_main_category
from transform.ingredient_identity import ingredient_keys
from transform.nutri_score import document_fields as nutri_score_fields
from transform.nutri_score import off_nutri_score
from transform.raw_records import RawRow, clean_rows, iter_off_rows
from transform.values import grade, optional_text, split_tags, strip_language, text, to_float, to_int

SOURCE = "off"
NORTH_AMERICA_COUNTRIES = ("canada", "united-states", "mexico")
_NUTRIMENT_SUFFIX = "_100g"


def off_product_documents(postgres: psycopg.Connection, stats: Counter) -> Iterator[dict[str, Any]]:
    rows = iter_off_rows(postgres, OFF_SOURCE, NORTH_AMERICA_COUNTRIES)
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
    nutriments = nutriments_per_100g(raw)
    cleaned = clean_name(name, remove_claims=True)
    source_category = main_category(raw, categories)
    return {
        "_id": identifiant,
        "identifiant": identifiant,
        "source": SOURCE,
        "produitDeBase": False,
        "codeBarres": code,
        "nomProduit": name,
        "nomNettoye": cleaned.name,
        "nomsAlternatifs": list(cleaned.alternative_names),
        "allegations": list(cleaned.claims),
        "nomGenerique": generic_name,
        "marque": ", ".join(brands),
        "marques": brands,
        "categorie": specific_main_category(source_category, categories),
        "categorieSource": source_category,
        "categories": categories,
        "categoriesPrecises": specific_categories(categories),
        **nutri_score_fields(off_nutri_score(raw, nutriments)),
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
        "nutriments": nutriments,
        "nutrimentsBase": "100 g",
        "cles": ingredient_keys(generic_name, name),
        "refBrut": row.reference(),
        "_chargeBrute": raw,
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


def main_category(raw: dict[str, Any], categories: list[str]) -> str:
    pnns_group = optional_text(raw.get("pnns_groups_1"))
    if pnns_group.casefold() == "unknown":
        pnns_group = ""
    fallback = categories[0] if categories else ""
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
