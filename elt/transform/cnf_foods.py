from __future__ import annotations

import psycopg
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import partial
from typing import Any

from extract.extract import CNF_SOURCE
from transform.description_cleaning import clean_name
from transform.ingredient_identity import ingredient_keys
from transform.nutri_score import cnf_nutri_score
from transform.nutri_score import document_fields as nutri_score_fields
from transform.raw_records import RawRow, clean_rows, iter_payloads, iter_raw_rows
from transform.values import french_or_english, optional_text, text, to_float, to_int

SOURCE = "cnf"

Lookup = dict[str, dict[str, Any]]
PerFood = dict[str, list[dict[str, Any]]]


@dataclass(frozen=True)
class CnfLookups:
    groups: Lookup
    food_sources: Lookup
    nutrients: dict[str, dict[str, Any]]
    measures: PerFood
    refuse: PerFood
    yields: PerFood


def cnf_food_documents(postgres: psycopg.Connection, stats: Counter) -> Iterator[dict[str, Any]]:
    lookups = load_lookups(postgres)
    rows = iter_raw_rows(postgres, CNF_SOURCE, "FOOD NAME.csv")
    return clean_rows(rows, partial(clean_cnf_food, lookups=lookups), stats)


def clean_cnf_food(row: RawRow, lookups: CnfLookups) -> dict[str, Any] | None:
    food = row.payload
    food_id = text(food.get("FoodID"))
    english = text(food.get("FoodDescription"))
    french = text(food.get("FoodDescriptionF"))
    if not food_id or not (french or english):
        return None

    group_id = text(food.get("FoodGroupID"))
    group = lookups.groups.get(group_id, {})
    origin = lookups.food_sources.get(text(food.get("FoodSourceID")), {})
    nutrients = lookups.nutrients.get(food_id, {})
    identifiant = f"cnf:{food_id}"
    cleaned = clean_name(french or english, remove_claims=False)
    cleaned_english = clean_name(english, remove_claims=False) if english else None
    return {
        "_id": identifiant,
        "identifiant": identifiant,
        "source": SOURCE,
        "produitDeBase": True,
        "codeBarres": None,
        "nomProduit": french or english,
        "nomFr": french,
        "nomEn": english,
        "nomNettoye": cleaned.name,
        "nomEnNettoye": cleaned_english.name if cleaned_english else "",
        "nomsAlternatifs": list(
            dict.fromkeys(
                (*cleaned.alternative_names, *(cleaned_english.alternative_names if cleaned_english else ()))
            )
        ),
        "nomScientifique": optional_text(food.get("ScientificName")),
        "marque": None,
        "marques": [],
        "categorie": french_or_english(group, "FoodGroupName"),
        "categorieEn": optional_text(group.get("FoodGroupName")),
        "origineDonnee": french_or_english(origin, "FoodSourceDescription"),
        **nutri_score_fields(cnf_nutri_score(group_id, english, nutrients)),
        "nova": None,
        "ecoScore": None,
        "nutriments": nutrients,
        "nutrimentsBase": "100 g",
        "mesures": lookups.measures.get(food_id, []),
        "dechets": lookups.refuse.get(food_id, []),
        "rendements": lookups.yields.get(food_id, []),
        "cles": ingredient_keys(french, english),
        "refBrut": row.reference(),
        "_chargeBrute": food,
    }


def load_lookups(postgres: psycopg.Connection) -> CnfLookups:
    def table(name: str) -> Iterator[dict[str, Any]]:
        return iter_payloads(postgres, CNF_SOURCE, f"{name}.csv")

    return CnfLookups(
        groups=index_by(table("FOOD GROUP"), "FoodGroupID"),
        food_sources=index_by(table("FOOD SOURCE"), "FoodSourceID"),
        nutrients=nutrients_by_food(
            table("NUTRIENT AMOUNT"), index_by(table("NUTRIENT NAME"), "NutrientID")
        ),
        measures=measures_by_food(
            table("CONVERSION FACTOR"), index_by(table("MEASURE NAME"), "MeasureID")
        ),
        refuse=refuse_by_food(table("REFUSE AMOUNT"), index_by(table("REFUSE NAME"), "RefuseID")),
        yields=yields_by_food(table("YIELD AMOUNT"), index_by(table("YIELD NAME"), "YieldID")),
    )


def index_by(records: Iterable[dict[str, Any]], key: str) -> Lookup:
    return {text(record.get(key)): record for record in records}


def nutrients_by_food(amounts: Iterable[dict[str, Any]], names: Lookup) -> dict[str, dict[str, Any]]:
    nutrients: dict[str, dict[str, Any]] = defaultdict(dict)
    for amount in amounts:
        nutrient_id = text(amount.get("NutrientID"))
        meta = names.get(nutrient_id)
        entry = nutrient_entry(amount, meta) if meta else None
        if entry is None:
            continue
        bucket = nutrients[text(amount.get("FoodID"))]
        symbol = entry["symbole"]
        bucket[symbol if symbol not in bucket else f"{symbol}_{nutrient_id}"] = entry
    return nutrients


def nutrient_entry(amount: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any] | None:
    value = to_float(amount.get("NutrientValue"))
    if value is None:
        return None
    entry = {
        "code": text(meta.get("NutrientCode")),
        "symbole": text(meta.get("NutrientSymbol")) or text(meta.get("NutrientCode")),
        "nom": french_or_english(meta, "NutrientName"),
        "nomEn": text(meta.get("NutrientName")),
        "unite": text(meta.get("NutrientUnit")),
        "valeur": value,
        "erreurType": to_float(amount.get("StandardError")),
        "nbObservations": to_int(amount.get("NumberofObservations")),
    }
    return {field: value for field, value in entry.items() if value is not None}


def measures_by_food(conversions: Iterable[dict[str, Any]], names: Lookup) -> PerFood:
    measures: PerFood = defaultdict(list)
    for conversion in conversions:
        factor = to_float(conversion.get("ConversionFactorValue"))
        if factor is None:
            continue
        measure_id = text(conversion.get("MeasureID"))
        measure = names.get(measure_id, {})
        measures[text(conversion.get("FoodID"))].append(
            {
                "mesureId": measure_id,
                "description": french_or_english(measure, "MeasureDescription"),
                "descriptionEn": text(measure.get("MeasureDescription")),
                "facteur": factor,
                "grammes": round(factor * 100, 4),
            }
        )
    return measures


def refuse_by_food(amounts: Iterable[dict[str, Any]], names: Lookup) -> PerFood:
    refuse: PerFood = defaultdict(list)
    for amount in amounts:
        name = names.get(text(amount.get("RefuseID")), {})
        refuse[text(amount.get("FoodID"))].append(
            {
                "description": french_or_english(name, "RefuseDescription"),
                "descriptionEn": text(name.get("RefuseDescription")),
                "pourcentage": to_float(amount.get("RefuseAmount")),
            }
        )
    return refuse


def yields_by_food(amounts: Iterable[dict[str, Any]], names: Lookup) -> PerFood:
    yields: PerFood = defaultdict(list)
    for amount in amounts:
        name = names.get(text(amount.get("YieldID")), {})
        yields[text(amount.get("FoodID"))].append(
            {
                "description": french_or_english(name, "YieldDescription"),
                "descriptionEn": text(name.get("YieldDescription")),
                "valeur": to_float(amount.get("YieldAmount")),
            }
        )
    return yields
