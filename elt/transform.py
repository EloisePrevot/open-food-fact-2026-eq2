"""Transformation: nettoie et met en forme les données extraites."""

from __future__ import annotations

from elt.config import Settings
from elt.connections import DatabaseConnections


def open_transformation_connections(settings: Settings | None = None) -> DatabaseConnections:
    """Ouvre les moteurs nécessaires au rejeu des transformations, sans les exécuter."""
    return DatabaseConnections.connect(settings or Settings.from_environment())
