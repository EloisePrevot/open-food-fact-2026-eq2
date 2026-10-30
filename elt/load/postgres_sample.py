"""Copie de la couche brute réduite à l'échantillon servi, pour la publier.

L'export complet d'Open Food Facts pèse 10 Go dans PostgreSQL. On publie
seulement les enregistrements bruts dont MongoDB a tiré un document (``refBrut``),
plus tout le FCEN, dont la transformation lit chaque fichier (nutriments, mesures).
``raw_artifacts`` est copiée telle quelle : les empreintes des fichiers sources
restent celles de l'état de chargement de MongoDB et de Qdrant, si bien que le
pipeline lancé au démarrage les juge à jour et ne recharge rien.

La copie est écrite dans une base séparée, ensuite exportée par
``docker compose run --rm postgres-dump``.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo
from pymongo.collection import Collection
from pymongo.database import Database

from config import Settings
from extract.extract import CNF_SOURCE, OFF_SOURCE
from load.mongo_storage import COLLECTIONS
from off_storage import ORDINAL_COLUMN, TABLE as OFF_TABLE, add_primary_key, recreate_table
from raw_storage import RawDataStore
from transform.off_products import SOURCE as OFF_DOCUMENT_SOURCE
from transform.transform import PRODUCT, RECIPE

SAMPLE_DATABASE = "open_food_facts_echantillon"
_ADMIN_DATABASE = "postgres"
_REFERENCE_FIELD = "refBrut"
_RECIPE_REFERENCES = "echantillon_recettes"
_OFF_REFERENCES = "echantillon_off"
_ARTIFACT_COLUMNS = (
    "artifact_id",
    "source",
    "relative_path",
    "media_type",
    "encoding",
    "sha256",
    "imported_at",
    "record_count",
)
_RECORD_COLUMNS = sql.SQL(", ").join(
    map(sql.Identifier, ("artifact_id", "record_ordinal", "payload_json", "payload_sha256"))
)


def export_postgres_sample(settings: Settings, mongo: Database) -> dict[str, int]:
    _recreate_sample_database(settings.postgres_dsn)
    with (
        psycopg.connect(settings.postgres_dsn) as source,
        psycopg.connect(make_conninfo(settings.postgres_dsn, dbname=SAMPLE_DATABASE)) as target,
    ):
        store = RawDataStore(target)
        store.initialize_schema()
        _copy_artifacts(source, target)
        _stage_references(source, _RECIPE_REFERENCES, _references(mongo[COLLECTIONS[RECIPE]], {}))
        _stage_references(
            source, _OFF_REFERENCES, _references(mongo[COLLECTIONS[PRODUCT]], {"source": OFF_DOCUMENT_SOURCE})
        )
        summary = {
            "enregistrementsBruts": _copy_raw_records(source, target),
            "produitsOff": _copy_off_products(source, target),
        }
        store.create_indexes()
        target.commit()
    return summary


def _recreate_sample_database(postgres_dsn: str) -> None:
    admin_dsn = make_conninfo(postgres_dsn, dbname=_ADMIN_DATABASE)
    with psycopg.connect(admin_dsn, autocommit=True) as admin:
        name = sql.Identifier(SAMPLE_DATABASE)
        admin.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(name))
        admin.execute(sql.SQL("CREATE DATABASE {}").format(name))


def _copy_artifacts(source: psycopg.Connection, target: psycopg.Connection) -> None:
    columns = sql.SQL(", ").join(map(sql.Identifier, _ARTIFACT_COLUMNS))
    rows = source.execute(sql.SQL("SELECT {} FROM raw_artifacts ORDER BY artifact_id").format(columns))
    placeholders = sql.SQL(", ").join(sql.Placeholder() * len(_ARTIFACT_COLUMNS))
    with target.cursor() as cursor:
        cursor.executemany(
            sql.SQL("INSERT INTO raw_artifacts ({}) OVERRIDING SYSTEM VALUE VALUES ({})").format(
                columns, placeholders
            ),
            rows.fetchall(),
        )
    target.execute(
        "SELECT setval(pg_get_serial_sequence('raw_artifacts', 'artifact_id'), "
        "COALESCE((SELECT MAX(artifact_id) FROM raw_artifacts), 1))"
    )


def _references(collection: Collection, query: dict[str, Any]) -> Iterable[tuple[int, int]]:
    selection = {**query, _REFERENCE_FIELD: {"$exists": True}}
    for document in collection.find(selection, {_REFERENCE_FIELD: 1}):
        reference = document[_REFERENCE_FIELD]
        yield reference["artifactId"], reference["ordinal"]


def _stage_references(
    source: psycopg.Connection, table: str, references: Iterable[tuple[int, int]]
) -> None:
    name = sql.Identifier(table)
    source.execute(
        sql.SQL(
            "CREATE TEMP TABLE {} (artifact_id BIGINT, record_ordinal BIGINT, "
            "PRIMARY KEY (artifact_id, record_ordinal))"
        ).format(name)
    )
    with source.cursor() as cursor, cursor.copy(sql.SQL("COPY {} FROM STDIN").format(name)) as copy:
        for reference in references:
            copy.write_row(reference)


def _copy_raw_records(source: psycopg.Connection, target: psycopg.Connection) -> int:
    """Tout le FCEN, plus les recettes de l'échantillon."""
    selection = sql.SQL(
        "SELECT {columns} FROM raw_records "
        "WHERE artifact_id IN (SELECT artifact_id FROM raw_artifacts WHERE source = {cnf}) "
        "UNION ALL "
        "SELECT {columns} FROM raw_records JOIN {recipes} USING (artifact_id, record_ordinal)"
    ).format(
        columns=_RECORD_COLUMNS,
        cnf=sql.Literal(CNF_SOURCE),
        recipes=sql.Identifier(_RECIPE_REFERENCES),
    )
    insertion = sql.SQL("COPY raw_records ({}) FROM STDIN").format(_RECORD_COLUMNS)
    _stream(source, target, selection, insertion)
    return target.execute("SELECT count(*) FROM raw_records").fetchone()[0]


def _copy_off_products(source: psycopg.Connection, target: psycopg.Connection) -> int:
    if source.execute("SELECT to_regclass(%s)", (OFF_TABLE,)).fetchone()[0] is None:
        return 0
    columns = [
        name
        for (name,) in source.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = current_schema() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (OFF_TABLE,),
        )
        if name != ORDINAL_COLUMN
    ]
    recreate_table(target, columns)
    off_artifact = source.execute(
        "SELECT MAX(artifact_id) FROM raw_artifacts WHERE source = %s", (OFF_SOURCE,)
    ).fetchone()[0]
    selection = sql.SQL(
        "SELECT product.* FROM {table} AS product "
        "JOIN {references} AS sample ON sample.record_ordinal = product.{ordinal} "
        "AND sample.artifact_id = {artifact}"
    ).format(
        table=sql.Identifier(OFF_TABLE),
        references=sql.Identifier(_OFF_REFERENCES),
        ordinal=sql.Identifier(ORDINAL_COLUMN),
        artifact=sql.Literal(off_artifact),
    )
    _stream(source, target, selection, sql.SQL("COPY {} FROM STDIN").format(sql.Identifier(OFF_TABLE)))
    add_primary_key(target)
    return target.execute(sql.SQL("SELECT count(*) FROM {}").format(sql.Identifier(OFF_TABLE))).fetchone()[0]


def _stream(
    source: psycopg.Connection, target: psycopg.Connection, selection: sql.Composable, insertion: sql.Composable
) -> None:
    copy_out = sql.SQL("COPY ({}) TO STDOUT").format(selection)
    with (
        source.cursor() as reader,
        reader.copy(copy_out) as rows_out,
        target.cursor() as writer,
        writer.copy(insertion) as rows_in,
    ):
        for chunk in rows_out:
            rows_in.write(chunk)
