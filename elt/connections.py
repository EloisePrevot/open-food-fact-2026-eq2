"""Clients réutilisables pour SQLite, MongoDB et Qdrant."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from pymongo import MongoClient
from pymongo.database import Database
from qdrant_client import QdrantClient

from elt.config import Settings


@dataclass
class DatabaseConnections:
    """Clients ouverts vers les trois moteurs utilisés par le pipeline."""

    sqlite: sqlite3.Connection
    mongo_client: MongoClient
    mongo_database: Database
    qdrant: QdrantClient

    @classmethod
    def connect(cls, settings: Settings) -> DatabaseConnections:
        settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        sqlite_connection = sqlite3.connect(settings.sqlite_path)
        mongo_client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5_000)

        return cls(
            sqlite=sqlite_connection,
            mongo_client=mongo_client,
            mongo_database=mongo_client[settings.mongodb_database],
            qdrant=QdrantClient(url=settings.qdrant_url, timeout=5.0),
        )

    def verify_connections(self) -> None:
        """Exécute une opération sans effet de bord sur chaque moteur."""
        self.sqlite.execute("SELECT 1").fetchone()
        self.mongo_client.admin.command("ping")
        self.qdrant.get_collections()

    def close(self) -> None:
        self.sqlite.close()
        self.mongo_client.close()
        self.qdrant.close()

    def __enter__(self) -> DatabaseConnections:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
