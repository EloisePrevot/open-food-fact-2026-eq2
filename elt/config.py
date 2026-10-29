"""Configuration des connexions de données du pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Valeurs de connexion lues une seule fois au démarrage du pipeline."""

    raw_directory: Path
    off_file: Path
    postgres_dsn: str
    mongodb_uri: str
    mongodb_database: str
    qdrant_url: str
    snapshot_directory: Path

    @classmethod
    def from_environment(cls) -> Settings:
        pipeline_directory = Path(__file__).parent
        raw_directory = Path(getenv("ELT_RAW_DIRECTORY", pipeline_directory / "raw"))

        return cls(
            raw_directory=raw_directory,
            off_file=Path(getenv("ELT_OFF_FILE", raw_directory / "off.csv")),
            postgres_dsn=getenv(
                "POSTGRES_DSN",
                "postgresql://postgres:postgres@localhost:5432/open_food_facts",
            ),
            mongodb_uri=getenv(
                "MONGODB_URI",
                "mongodb://root:root@localhost:27017/?authSource=admin",
            ),
            mongodb_database=getenv("MONGODB_DATABASE", "open_food_facts"),
            qdrant_url=getenv("QDRANT_URL", "http://localhost:6333"),
            snapshot_directory=Path(
                getenv("ELT_SNAPSHOT_DIRECTORY", pipeline_directory / "snapshots")
            ),
        )
