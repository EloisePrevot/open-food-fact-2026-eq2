from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TRANSFORM_DIRECTORY = Path(__file__).parents[1] / "transform"


@dataclass(frozen=True)
class LoadState:
    version: str
    limit: int | None

    def covers(self, requested: LoadState) -> bool:
        return self.version == requested.version and _limit_covers(self.limit, requested.limit)

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "limite": self.limit}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> LoadState | None:
        if not data or "version" not in data:
            return None
        return cls(data["version"], data.get("limite"))


def requested_state(sqlite: sqlite3.Connection, raw_source: str, limit: int | None, *extras: str) -> LoadState:
    return LoadState(source_version(sqlite, raw_source, *extras), limit)


def is_up_to_date(loaded: LoadState | None, requested: LoadState) -> bool:
    return loaded is not None and loaded.covers(requested)


def source_version(sqlite: sqlite3.Connection, raw_source: str, *extras: str) -> str:
    digest = hashlib.sha256(_rules_fingerprint().encode())
    for part in (*extras, *_latest_artifacts(sqlite, raw_source)):
        digest.update(f"{part}\n".encode())
    return digest.hexdigest()


def _limit_covers(loaded: int | None, requested: int | None) -> bool:
    if loaded is None:
        return True
    return requested is not None and loaded >= requested


def _latest_artifacts(sqlite: sqlite3.Connection, raw_source: str) -> list[str]:
    rows = sqlite.execute(
        """
        SELECT relative_path, sha256 FROM raw_artifacts AS artifact
        WHERE source = ? AND artifact_id = (
            SELECT MAX(artifact_id) FROM raw_artifacts
            WHERE source = artifact.source AND relative_path = artifact.relative_path
        )
        ORDER BY relative_path
        """,
        (raw_source,),
    )
    return [f"{path}:{sha256}" for path, sha256 in rows]


def _rules_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in sorted(TRANSFORM_DIRECTORY.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()
