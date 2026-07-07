"""SQLite state: dedupe + persistent print queue. Phase 1."""
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

    # queue enqueue/dequeue: Phase 2 (spooler persistence)
