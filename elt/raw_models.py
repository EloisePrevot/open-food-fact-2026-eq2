"""Modèles de la couche brute, indépendants des schémas applicatifs futurs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class RawArtifact:
    """Fichier source à conserver et indexer dans la couche brute."""

    source: str
    path: Path
    relative_path: str
    encoding: str
    media_type: str


@dataclass(frozen=True)
class RawRecord:
    """Enregistrement source avant toute transformation métier."""

    ordinal: int
    payload: Mapping[str, object]
