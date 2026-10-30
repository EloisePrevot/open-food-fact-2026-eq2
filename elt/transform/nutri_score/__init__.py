"""Nutri-Score 2023 : règles d'affaires et traduction des sources (OFF, FCEN)."""

from __future__ import annotations

from typing import Any

from transform.nutri_score.cnf_inputs import cnf_nutri_score
from transform.nutri_score.model import NutriScore
from transform.nutri_score.off_inputs import off_nutri_score

__all__ = ["NutriScore", "cnf_nutri_score", "document_fields", "off_nutri_score"]


def document_fields(nutri_score: NutriScore | None) -> dict[str, Any]:
    if nutri_score is None:
        return {"nutriScore": None, "nutriScoreValeur": None, "nutriScoreOrigine": None}
    return {
        "nutriScore": nutri_score.grade,
        "nutriScoreValeur": nutri_score.score,
        "nutriScoreOrigine": nutri_score.origin,
    }
