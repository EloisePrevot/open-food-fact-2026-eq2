from __future__ import annotations

import json
import sqlite3
from collections import Counter
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RawRow:
    artifact_id: int
    ordinal: int
    payload: dict[str, Any]

    def reference(self) -> dict[str, int]:
        return {"artifactId": self.artifact_id, "ordinal": self.ordinal}


Cleaner = Callable[[RawRow], "dict[str, Any] | None"]


def iter_raw_rows(
    sqlite: sqlite3.Connection,
    source: str,
    path_suffix: str = "",
    text_filters: tuple[str, ...] = (),
) -> Iterator[RawRow]:
    artifact_id = _latest_artifact_id(sqlite, source, path_suffix)
    if artifact_id is None:
        return
    parameters = [artifact_id, *(f"%{fragment}%" for fragment in text_filters)]
    for ordinal, payload_json in sqlite.execute(_records_query(text_filters), parameters):
        yield RawRow(artifact_id, ordinal, json.loads(payload_json))


def iter_payloads(sqlite: sqlite3.Connection, source: str, path_suffix: str) -> Iterator[dict[str, Any]]:
    return (row.payload for row in iter_raw_rows(sqlite, source, path_suffix))


def clean_rows(rows: Iterable[RawRow], cleaner: Cleaner, stats: Counter) -> Iterator[dict[str, Any]]:
    seen: set[str] = set()
    for row in rows:
        document = cleaner(row)
        outcome = _outcome(document, seen)
        stats[outcome] += 1
        if outcome == "conserves":
            seen.add(document["_id"])
            yield document


def _outcome(document: dict[str, Any] | None, seen: set[str]) -> str:
    if not document:
        return "rejetes"
    return "doublons" if document["_id"] in seen else "conserves"


def _latest_artifact_id(sqlite: sqlite3.Connection, source: str, path_suffix: str) -> int | None:
    row = sqlite.execute(
        """
        SELECT artifact_id FROM raw_artifacts
        WHERE source = ? AND relative_path LIKE ?
        ORDER BY artifact_id DESC LIMIT 1
        """,
        (source, f"%{path_suffix}"),
    ).fetchone()
    return None if row is None else row[0]


def _records_query(text_filters: tuple[str, ...]) -> str:
    query = "SELECT record_ordinal, payload_json FROM raw_records WHERE artifact_id = ?"
    if not text_filters:
        return query
    return query + " AND (" + " OR ".join("payload_json LIKE ?" for _ in text_filters) + ")"
