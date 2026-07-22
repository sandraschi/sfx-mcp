from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path


class SoundCache:
    """SQLite-backed local cache for downloaded sounds and user tags."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sounds (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    duration REAL,
                    samplerate REAL,
                    tags TEXT,
                    local_path TEXT,
                    downloaded_at TEXT
                );
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sound_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (sound_id) REFERENCES sounds(id),
                    UNIQUE(sound_id, tag)
                );
                CREATE INDEX IF NOT EXISTS idx_tags_sound ON tags(sound_id);
                CREATE INDEX IF NOT EXISTS idx_tag_name ON tags(tag);
            """)

    def add_sound(
        self,
        sound_id: int,
        name: str,
        description: str = "",
        duration: float = 0.0,
        samplerate: float = 0.0,
        tags: list[str] | None = None,
        local_path: str = "",
    ) -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO sounds
                   (id, name, description, duration, samplerate, tags, local_path, downloaded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sound_id,
                    name,
                    description,
                    duration,
                    samplerate,
                    json.dumps(tags or []),
                    local_path,
                    datetime.utcnow().isoformat(),
                ),
            )

    def add_tag(self, sound_id: int, tag: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tags (sound_id, tag) VALUES (?, ?)",
                (sound_id, tag.lower().strip()),
            )

    def list_local(self, tag_filter: str | None = None) -> list[dict]:
        with self._conn() as conn:
            if tag_filter:
                rows = conn.execute(
                    """SELECT DISTINCT s.* FROM sounds s
                       JOIN tags t ON t.sound_id = s.id
                       WHERE t.tag = ?
                       ORDER BY s.downloaded_at DESC""",
                    (tag_filter.lower().strip(),),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM sounds ORDER BY downloaded_at DESC"
                ).fetchall()
            results = []
            for row in rows:
                d = dict(row)
                d["tags"] = json.loads(d.get("tags") or "[]")
                user_tags = conn.execute(
                    "SELECT tag FROM tags WHERE sound_id = ?", (d["id"],)
                ).fetchall()
                d["user_tags"] = [t["tag"] for t in user_tags]
                results.append(d)
            return results

    def get_sound(self, sound_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM sounds WHERE id = ?", (sound_id,)
            ).fetchone()
            if row is None:
                return None
            d = dict(row)
            d["tags"] = json.loads(d.get("tags") or "[]")
            user_tags = conn.execute(
                "SELECT tag FROM tags WHERE sound_id = ?", (sound_id,)
            ).fetchall()
            d["user_tags"] = [t["tag"] for t in user_tags]
            return d

    def sound_exists(self, sound_id: int) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM sounds WHERE id = ?", (sound_id,)
            ).fetchone()
            return row is not None
