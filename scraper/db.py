from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


LOGGER = logging.getLogger(__name__)
DB_PATH = Path("scraper.db")


MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS channels (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        subscriber_count INTEGER,
        long_form_videos INTEGER DEFAULT 0,
        last_longform_upload TEXT,
        language_code TEXT,
        telegram TEXT,
        emails TEXT,
        blacklisted INTEGER DEFAULT 0,
        blacklist_reason TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        quality_score REAL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        channel_id TEXT,
        title TEXT,
        description TEXT,
        tags TEXT,
        is_short INTEGER DEFAULT 0,
        is_live INTEGER DEFAULT 0,
        language_code TEXT,
        published_at TEXT,
        metadata TEXT,
        FOREIGN KEY(channel_id) REFERENCES channels(id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS discovery_state (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS enrichment_settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        payload TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """,
]


class Database:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self._apply_migrations()

    def _apply_migrations(self) -> None:
        with self.conn:
            for index, migration in enumerate(MIGRATIONS):
                LOGGER.debug("Applying migration %s", index)
                self.conn.executescript(migration)
        self.set_meta("schema_version", str(len(MIGRATIONS)))

    def set_meta(self, key: str, value: str) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_meta(self, key: str, default: Optional[str] = None) -> Optional[str]:
        cursor = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    def persist_discovery_state(self, state: Mapping[str, Any]) -> None:
        with self.conn:
            for key, value in state.items():
                self.conn.execute(
                    "INSERT INTO discovery_state (key, value) VALUES (?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
                    (key, json.dumps(value)),
                )

    def load_discovery_state(self) -> dict[str, Any]:
        cursor = self.conn.execute("SELECT key, value FROM discovery_state")
        return {row["key"]: json.loads(row["value"]) for row in cursor.fetchall()}

    def upsert_channel(self, channel: Mapping[str, Any]) -> None:
        payload = {**channel}
        payload.setdefault("emails", json.dumps([]))
        payload.setdefault("blacklisted", 0)
        with self.conn:
            columns = ",".join(payload.keys())
            placeholders = ",".join([":" + key for key in payload.keys()])
            update = ",".join([f"{key}=excluded.{key}" for key in payload.keys() if key != "id"])
            sql = (
                f"INSERT INTO channels ({columns}) VALUES ({placeholders}) "
                f"ON CONFLICT(id) DO UPDATE SET {update}, updated_at = CURRENT_TIMESTAMP"
            )
            self.conn.execute(sql, payload)

    def bulk_insert_videos(self, videos: Iterable[Mapping[str, Any]]) -> None:
        with self.conn:
            for video in videos:
                payload = {**video}
                payload.setdefault("metadata", json.dumps({}))
                payload.setdefault("tags", json.dumps(video.get("tags", [])))
                self.conn.execute(
                    "INSERT INTO videos (id, channel_id, title, description, tags, is_short, is_live, language_code, published_at, metadata) "
                    "VALUES (:id, :channel_id, :title, :description, :tags, :is_short, :is_live, :language_code, :published_at, :metadata) "
                    "ON CONFLICT(id) DO UPDATE SET title = excluded.title, description = excluded.description, tags = excluded.tags, "
                    "is_short = excluded.is_short, is_live = excluded.is_live, language_code = excluded.language_code, published_at = excluded.published_at, metadata = excluded.metadata",
                    payload,
                )

    def record_log(self, category: str, details: Mapping[str, Any]) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO logs (category, details) VALUES (?, ?)",
                (category, json.dumps(details)),
            )

    def load_enrichment_settings(self) -> dict[str, Any]:
        cursor = self.conn.execute("SELECT payload FROM enrichment_settings WHERE id = 1")
        row = cursor.fetchone()
        if not row:
            return {}
        return json.loads(row[0])

    def save_enrichment_settings(self, payload: Mapping[str, Any]) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO enrichment_settings (id, payload) VALUES (1, ?) "
                "ON CONFLICT(id) DO UPDATE SET payload = excluded.payload, updated_at = CURRENT_TIMESTAMP",
                (json.dumps(payload),),
            )

    def export_bundle(self, data_path: Path) -> None:
        payload = {
            "channels": [dict(row) for row in self.conn.execute("SELECT * FROM channels")],
            "videos": [dict(row) for row in self.conn.execute("SELECT * FROM videos")],
            "discovery_state": self.load_discovery_state(),
        }
        data_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        meta = {"schema_version": self.get_meta("schema_version", "0"), "quality_prepared": True}
        data_path.with_name("meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def import_bundle(self, data_path: Path) -> None:
        payload = json.loads(data_path.read_text(encoding="utf-8"))
        with self.conn:
            for channel in payload.get("channels", []):
                self.upsert_channel(channel)
            for video in payload.get("videos", []):
                self.bulk_insert_videos([video])
            if state := payload.get("discovery_state"):
                self.persist_discovery_state(state)


def ensure_db() -> Database:
    return Database()


__all__ = ["Database", "ensure_db", "DB_PATH"]
