"""Clients réutilisables pour PostgreSQL, MongoDB et Qdrant."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg
from pymongo import MongoClient
from pymongo.database import Database
from qdrant_client import QdrantClient

from elt.config import Settings


def open_postgres_connection(settings: Settings) -> psycopg.Connection:
    """Ouvre une connexion PostgreSQL au DSN configuré."""
    return psycopg.connect(settings.postgres_dsn)


@dataclass
class DatabaseConnections:
    """Clients ouverts vers les trois moteurs utilisés par le pipeline."""

    postgres: psycopg.Connection
    mongo_client: MongoClient
    mongo_database: Database
    qdrant: QdrantClient

    @classmethod
    def connect(cls, settings: Settings) -> DatabaseConnections:
        mongo_client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5_000)

        return cls(
            postgres=open_postgres_connection(settings),
            mongo_client=mongo_client,
            mongo_database=mongo_client[settings.mongodb_database],
            qdrant=QdrantClient(url=settings.qdrant_url, timeout=5.0),
        )

    def verify_connections(self) -> None:
        """Exécute une opération sans effet de bord sur chaque moteur."""
        self.postgres.execute("SELECT 1").fetchone()
        self.mongo_client.admin.command("ping")
        self.qdrant.get_collections()

    def close(self) -> None:
        self.postgres.close()
        self.mongo_client.close()
        self.qdrant.close()

    def __enter__(self) -> DatabaseConnections:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
