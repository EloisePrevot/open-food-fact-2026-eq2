"""Stockage PostgreSQL append-only des artefacts et enregistrements bruts.

La couche brute est reconstruite à partir des sources, jamais modifiée en place.
On optimise donc le chargement pour la vitesse :

* tables ``UNLOGGED`` : pas de journal WAL, parfait pour des données rejouables ;
* ``COPY ... FROM STDIN`` au lieu de ``INSERT``, bien plus rapide en masse ;
* index secondaires créés une seule fois, après le chargement.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from datetime import UTC, datetime

import psycopg

from elt.raw_models import RawArtifact, RawRecord


class RawDataStore:
    """Persiste les données brutes sans leur appliquer de règle métier."""

    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection

    def initialize_schema(self) -> None:
        """Crée les tables brutes (UNLOGGED) sans les index secondaires."""
        self._connection.execute(
            """
            CREATE UNLOGGED TABLE IF NOT EXISTS raw_artifacts (
                artifact_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                source        TEXT        NOT NULL,
                relative_path TEXT        NOT NULL,
                media_type    TEXT        NOT NULL,
                encoding      TEXT        NOT NULL,
                sha256        TEXT        NOT NULL,
                imported_at   TIMESTAMPTZ NOT NULL,
                record_count  BIGINT      NOT NULL DEFAULT 0,
                UNIQUE (source, relative_path, sha256)
            );
            """
        )
        self._connection.execute(
            """
            CREATE UNLOGGED TABLE IF NOT EXISTS raw_records (
                artifact_id    BIGINT NOT NULL REFERENCES raw_artifacts(artifact_id),
                record_ordinal BIGINT NOT NULL,
                payload_json   JSONB  NOT NULL,
                payload_sha256 TEXT   NOT NULL,
                PRIMARY KEY (artifact_id, record_ordinal)
            );
            """
        )
        self._connection.commit()

    def create_indexes(self) -> None:
        """Crée les index secondaires une fois le chargement terminé."""
        self._connection.execute(
            """
            CREATE INDEX IF NOT EXISTS raw_records_payload_sha256_index
                ON raw_records (artifact_id, payload_sha256);
            """
        )
        # Index par source : le chargement de la BD2/BD3 sélectionne une source
        # (recettes, CNF, OFF) en lisant cet index plutôt qu'en balayant toute
        # la table raw_artifacts. Les enregistrements d'un artefact sont ensuite
        # lus via la clé primaire (artifact_id, record_ordinal), déjà indexée.
        self._connection.execute(
            """
            CREATE INDEX IF NOT EXISTS raw_artifacts_source_index
                ON raw_artifacts (source);
            """
        )
        self._connection.commit()

    def ingest(self, artifact: RawArtifact, records: Iterable[RawRecord]) -> int:
        """Enregistre un artefact une seule fois par contenu et chemin source."""
        artifact_hash = self._hash_file(artifact)

        with self._connection.transaction():
            existing_artifact = self._connection.execute(
                """
                SELECT artifact_id
                FROM raw_artifacts
                WHERE source = %s AND relative_path = %s AND sha256 = %s
                """,
                (artifact.source, artifact.relative_path, artifact_hash),
            ).fetchone()

            if existing_artifact is not None:
                return 0

            artifact_id = self._connection.execute(
                """
                INSERT INTO raw_artifacts (
                    source, relative_path, media_type, encoding, sha256, imported_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING artifact_id
                """,
                (
                    artifact.source,
                    artifact.relative_path,
                    artifact.media_type,
                    artifact.encoding,
                    artifact_hash,
                    datetime.now(UTC),
                ),
            ).fetchone()[0]

            record_count = self._copy_records(artifact_id, records)

            self._connection.execute(
                "UPDATE raw_artifacts SET record_count = %s WHERE artifact_id = %s",
                (record_count, artifact_id),
            )

        return record_count

    def _copy_records(self, artifact_id: int, records: Iterable[RawRecord]) -> int:
        """Charge les enregistrements via COPY FROM STDIN (chemin le plus rapide)."""
        record_count = 0

        with self._connection.cursor() as cursor:
            with cursor.copy(
                """
                COPY raw_records (
                    artifact_id, record_ordinal, payload_json, payload_sha256
                ) FROM STDIN
                """
            ) as copy:
                for record in records:
                    payload_json = json.dumps(
                        record.payload,
                        ensure_ascii=False,
                        separators=(",", ":"),
                        allow_nan=False,
                    )
                    payload_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
                    copy.write_row(
                        (artifact_id, record.ordinal, payload_json, payload_sha256)
                    )
                    record_count += 1

        return record_count

    @staticmethod
    def _hash_file(artifact: RawArtifact) -> str:
        digest = hashlib.sha256()
        with artifact.path.open("rb") as source_file:
            for chunk in iter(lambda: source_file.read(1_048_576), b""):
                digest.update(chunk)

        return digest.hexdigest()

    def _insert_batch(self, batch: list[tuple[int, int, str, str]]) -> None:
        self._connection.executemany(
            """
            INSERT INTO raw_records (
                artifact_id, record_ordinal, payload_json, payload_sha256
            ) VALUES (?, ?, ?, ?)
            """,
            batch,
        )