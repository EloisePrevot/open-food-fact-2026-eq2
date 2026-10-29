from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from itertools import count
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from off_storage import ORDINAL_COLUMN, TABLE as OFF_TABLE

_FETCH_SIZE = 5_000
_cursor_numbers = count()


@dataclass(frozen=True)
class RawRow:
    artifact_id: int
    ordinal: int
    payload: dict[str, Any]

    def reference(self) -> dict[str, int]:
        return {"artifactId": self.artifact_id, "ordinal": self.ordinal}


Cleaner = Callable[[RawRow], "dict[str, Any] | None"]


def iter_raw_rows(postgres: psycopg.Connection, source: str, path_suffix: str = "") -> Iterator[RawRow]:
    artifact_id = latest_artifact_id(postgres, source, path_suffix)
    if artifact_id is None:
        return
    query = sql.SQL(
        "SELECT record_ordinal, payload_json FROM raw_records WHERE artifact_id = %s ORDER BY record_ordinal"
    )
    for ordinal, payload in _stream(postgres, query, (artifact_id,)):
        yield RawRow(artifact_id, ordinal, payload)


def iter_off_rows(postgres: psycopg.Connection, source: str, countries: tuple[str, ...]) -> Iterator[RawRow]:
    artifact_id = latest_artifact_id(postgres, source)
    if artifact_id is None:
        return
    query = sql.SQL("SELECT * FROM {} WHERE countries_tags ILIKE ANY(%s) ORDER BY {}").format(
        sql.Identifier(OFF_TABLE), sql.Identifier(ORDINAL_COLUMN)
    )
    patterns = [f"%{country}%" for country in countries]
    for row in _stream(postgres, query, (patterns,), dict_row):
        yield RawRow(artifact_id, row.pop(ORDINAL_COLUMN), row)


def iter_payloads(postgres: psycopg.Connection, source: str, path_suffix: str) -> Iterator[dict[str, Any]]:
    return (row.payload for row in iter_raw_rows(postgres, source, path_suffix))


def clean_rows(rows: Iterable[RawRow], cleaner: Cleaner, stats: Counter) -> Iterator[dict[str, Any]]:
    seen: set[str] = set()
    for row in rows:
        document = cleaner(row)
        outcome = _outcome(document, seen)
        stats[outcome] += 1
        if outcome == "conserves":
            seen.add(document["_id"])
            yield document


def latest_artifact_id(postgres: psycopg.Connection, source: str, path_suffix: str = "") -> int | None:
    row = postgres.execute(
        """
        SELECT artifact_id FROM raw_artifacts
        WHERE source = %s AND relative_path LIKE %s
        ORDER BY artifact_id DESC LIMIT 1
        """,
        (source, f"%{path_suffix}"),
    ).fetchone()
    return None if row is None else row[0]


def _outcome(document: dict[str, Any] | None, seen: set[str]) -> str:
    if not document:
        return "rejetes"
    return "doublons" if document["_id"] in seen else "conserves"


def _stream(
    postgres: psycopg.Connection, query: sql.Composable, parameters: tuple, row_factory: Any = None
) -> Iterator[Any]:
    with postgres.cursor(name=f"raw_rows_{next(_cursor_numbers)}", row_factory=row_factory) as cursor:
        cursor.itersize = _FETCH_SIZE
        cursor.execute(query, parameters)
        yield from cursor
