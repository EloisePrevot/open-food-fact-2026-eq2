"""Stockage SQLite append-only des artefacts et enregistrements bruts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime

from raw_models import RawArtifact, RawRecord


class RawDataStore:
    """Persiste les données brutes sans leur appliquer de règle métier."""

    _INSERT_BATCH_SIZE = 1_000

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def initialize_schema(self) -> None:
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_artifacts (
                artifact_id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                media_type TEXT NOT NULL,
                encoding TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                imported_at TEXT NOT NULL,
                record_count INTEGER NOT NULL DEFAULT 0,
                UNIQUE(source, relative_path, sha256)
            );

            CREATE TABLE IF NOT EXISTS raw_records (
                artifact_id INTEGER NOT NULL,
                record_ordinal INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                PRIMARY KEY (artifact_id, record_ordinal),
                FOREIGN KEY (artifact_id) REFERENCES raw_artifacts(artifact_id)
            );

            CREATE INDEX IF NOT EXISTS raw_records_payload_sha256_index
                ON raw_records(artifact_id, payload_sha256);
            """
        )

    def ingest(self, artifact: RawArtifact, records: Iterable[RawRecord]) -> int:
        """Enregistre un artefact une seule fois par contenu et chemin source."""
        artifact_hash = self._hash_file(artifact)
        existing_artifact = self._connection.execute(
            """
            SELECT artifact_id
            FROM raw_artifacts
            WHERE source = ? AND relative_path = ? AND sha256 = ?
            """,
            (artifact.source, artifact.relative_path, artifact_hash),
        ).fetchone()

        if existing_artifact is not None:
            return 0

        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT INTO raw_artifacts (
                    source, relative_path, media_type, encoding, sha256, imported_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.source,
                    artifact.relative_path,
                    artifact.media_type,
                    artifact.encoding,
                    artifact_hash,
                    datetime.now(UTC).isoformat(),
                ),
            )
            artifact_id = cursor.lastrowid
            record_count = self._insert_records(artifact_id, records)
            self._connection.execute(
                "UPDATE raw_artifacts SET record_count = ? WHERE artifact_id = ?",
                (record_count, artifact_id),
            )

        return record_count

    def _insert_records(self, artifact_id: int, records: Iterable[RawRecord]) -> int:
        batch: list[tuple[int, int, str, str]] = []
        record_count = 0

        for record in records:
            payload_json = json.dumps(
                record.payload,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            )
            batch.append(
                (
                    artifact_id,
                    record.ordinal,
                    payload_json,
                    hashlib.sha256(payload_json.encode("utf-8")).hexdigest(),
                )
            )
            record_count += 1

            if len(batch) == self._INSERT_BATCH_SIZE:
                self._insert_batch(batch)
                batch.clear()

        if batch:
            self._insert_batch(batch)

        return record_count

    def _insert_batch(self, batch: list[tuple[int, int, str, str]]) -> None:
        self._connection.executemany(
            """
            INSERT INTO raw_records (
                artifact_id, record_ordinal, payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?)
            """,
            batch,
        )

    @staticmethod
    def _hash_file(artifact: RawArtifact) -> str:
        digest = hashlib.sha256()
        with artifact.path.open("rb") as source_file:
            for chunk in iter(lambda: source_file.read(1_048_576), b""):
                digest.update(chunk)

        return digest.hexdigest()
