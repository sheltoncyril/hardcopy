"""SQLite state: dedupe + persistent print queue."""
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen  (id TEXT PRIMARY KEY, at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS queue (id TEXT PRIMARY KEY, event_json TEXT, at TEXT DEFAULT CURRENT_TIMESTAMP);
"""


class Store:
    def __init__(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)

    def is_new(self, event_id: str) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO seen (id) VALUES (?)", (event_id,)
        )
        self.db.commit()
        return cur.rowcount == 1

    def enqueue(self, event_id: str, event_json: str) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO queue (id, event_json) VALUES (?, ?)",
            (event_id, event_json),
        )
        self.db.commit()

    def dequeue_all(self) -> list[tuple[str, str]]:
        rows = self.db.execute(
            "SELECT id, event_json FROM queue ORDER BY at"
        ).fetchall()
        return rows

    def remove_queued(self, event_id: str) -> None:
        self.db.execute("DELETE FROM queue WHERE id = ?", (event_id,))
        self.db.commit()
