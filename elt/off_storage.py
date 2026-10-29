"""Table PostgreSQL typée pour l'export Open Food Facts complet.

Chaque colonne du TSV devient une colonne ``TEXT`` de ``off_products`` (nom
d'origine conservé). Aucun filtre n'est appliqué ici : la sélection des
produits nord-américains se fait dans la transformation vers MongoDB.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import chain

import psycopg
from psycopg import sql

from raw_models import RawRecord

TABLE = "off_products"
ORDINAL_COLUMN = "record_ordinal"


def replace_off_products(connection: psycopg.Connection, records: Iterable[RawRecord]) -> int:
    """Remplace le contenu de off_products par les enregistrements fournis."""
    iterator = iter(records)
    first = next(iterator, None)
    columns = list(first.payload) if first else []
    _recreate_table(connection, columns)
    if first is None:
        return 0
    count = _copy_rows(connection, columns, chain([first], iterator))
    connection.execute(
        sql.SQL("ALTER TABLE {} ADD PRIMARY KEY ({})").format(
            sql.Identifier(TABLE), sql.Identifier(ORDINAL_COLUMN)
        )
    )
    return count


def _recreate_table(connection: psycopg.Connection, columns: list[str]) -> None:
    definitions = [sql.SQL("{} BIGINT NOT NULL").format(sql.Identifier(ORDINAL_COLUMN))]
    definitions += [sql.SQL("{} TEXT").format(sql.Identifier(column)) for column in columns]
    connection.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(TABLE)))
    connection.execute(
        sql.SQL("CREATE UNLOGGED TABLE {} ({})").format(
            sql.Identifier(TABLE), sql.SQL(", ").join(definitions)
        )
    )


def _copy_rows(connection: psycopg.Connection, columns: list[str], records: Iterator[RawRecord]) -> int:
    count = 0
    with connection.cursor() as cursor, cursor.copy(_copy_statement(columns)) as copy:
        for record in records:
            copy.write_row(_row(record, columns))
            count += 1
    return count


def _copy_statement(columns: list[str]) -> sql.Composed:
    return sql.SQL("COPY {} ({}) FROM STDIN").format(
        sql.Identifier(TABLE),
        sql.SQL(", ").join(sql.Identifier(column) for column in [ORDINAL_COLUMN, *columns]),
    )


def _row(record: RawRecord, columns: list[str]) -> list[object]:
    return [record.ordinal, *(_value(record.payload.get(column)) for column in columns)]


def _value(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value).replace("\x00", "")
