from __future__ import annotations

import json

class RawStoreAdapter:
    def __init__(self, sqlite_conn):
        self.sqlite_conn = sqlite_conn

    def get_recipes(self) -> list[dict]:
        cursor = self.sqlite_conn.execute("SELECT payload_json FROM raw_records")
        return [json.loads(row[0]) for row in cursor.fetchall()]

    def get_ingredients(self) -> list[dict]:
        cursor = self.sqlite_conn.execute("SELECT payload_json FROM raw_records")
        return [json.loads(row[0]) for row in cursor.fetchall()]