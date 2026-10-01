"""Configuration des connexions de données du pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Valeurs de connexion lues une seule fois au démarrage du pipeline."""

    sqlite_path: Path
    mongodb_uri: str
    mongodb_database: str
    qdrant_url: str

    @classmethod
    def from_environment(cls) -> Settings:
        data_directory = Path(getenv("ELT_DATA_DIRECTORY", Path(__file__).parent / "data"))

        return cls(
            sqlite_path=Path(getenv("SQLITE_PATH", data_directory / "raw-data.db")),
            mongodb_uri=getenv(
                "MONGODB_URI",
                "mongodb://root:root@localhost:27017/?authSource=admin",
            ),
            mongodb_database=getenv("MONGODB_DATABASE", "open_food_facts"),
            qdrant_url=getenv("QDRANT_URL", "http://localhost:6333"),
        )
