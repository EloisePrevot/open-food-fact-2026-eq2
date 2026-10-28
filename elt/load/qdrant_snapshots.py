from __future__ import annotations

import json
import shutil
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote

from qdrant_client import QdrantClient

from load.qdrant_storage import COLLECTIONS, EMBEDDING_MODEL

MANIFEST_FILE = "manifest.json"
DOWNLOAD_CHUNK_SIZE = 1 << 20


def export_snapshots(client: QdrantClient, qdrant_url: str, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    collections = {name: export_collection(client, qdrant_url, name, directory) for name in COLLECTIONS.values()}
    manifest = directory / MANIFEST_FILE
    manifest.write_text(json.dumps(_manifest(client, collections), indent=2), encoding="utf-8")
    return manifest


def export_collection(client: QdrantClient, qdrant_url: str, collection: str, directory: Path) -> dict:
    print(f"Snapshot {collection}...")
    snapshot = client.create_snapshot(collection_name=collection, wait=True)
    target = directory / f"{collection}.snapshot"
    _download(f"{qdrant_url}/collections/{collection}/snapshots/{quote(snapshot.name)}", target)
    client.delete_snapshot(collection_name=collection, snapshot_name=snapshot.name, wait=True)
    return {
        "fichier": target.name,
        "points": client.count(collection_name=collection, exact=True).count,
        "octets": target.stat().st_size,
    }


def _download(url: str, target: Path) -> None:
    partial = target.with_name(target.name + ".part")
    with urllib.request.urlopen(url) as response, partial.open("wb") as file:
        shutil.copyfileobj(response, file, DOWNLOAD_CHUNK_SIZE)
    partial.replace(target)


def _manifest(client: QdrantClient, collections: dict[str, dict]) -> dict:
    return {
        "qdrantVersion": client.info().version,
        "modeleEmbedding": EMBEDDING_MODEL,
        "creeLe": datetime.now(UTC).isoformat(),
        "collections": collections,
    }
