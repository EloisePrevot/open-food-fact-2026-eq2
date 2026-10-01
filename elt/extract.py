"""Extraction: récupère les données brutes des sources externes."""

from __future__ import annotations

from elt.config import Settings
from elt.connections import DatabaseConnections


def open_extraction_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs disponibles au futur extracteur, sans extraire de données."""
    return DatabaseConnections.connect(settings or Settings.from_environment())
