"""SQLite access layer. All SQL lives here.

Numbers are stored sorted ascending (n1 < n2 < ... < n6).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import DB_PATH, ensure_data_dir
from .models import Draw, Pick

SCHEMA_VERSION = "1"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS draws (
    draw_id     TEXT PRIMARY KEY,
    draw_date   TEXT NOT NULL,
    n1 INTEGER NOT NULL, n2 INTEGER NOT NULL, n3 INTEGER NOT NULL,
    n4 INTEGER NOT NULL, n5 INTEGER NOT NULL, n6 INTEGER NOT NULL,
    extra       INTEGER NOT NULL,
    jackpot     INTEGER,
    CHECK (n1 BETWEEN 1 AND 59), CHECK (n2 BETWEEN 1 AND 59),
    CHECK (n3 BETWEEN 1 AND 59), CHECK (n4 BETWEEN 1 AND 59),
    CHECK (n5 BETWEEN 1 AND 59), CHECK (n6 BETWEEN 1 AND 59),
    CHECK (extra BETWEEN 1 AND 59)
);

CREATE TABLE IF NOT EXISTS saved_picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    numbers TEXT NOT NULL,
    method TEXT NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class Database:
    """Thin wrapper around a single SQLite connection."""

    def __init__(self, path: Path | str = DB_PATH):
        self.path = Path(path)
        if str(path) != ":memory:":
            ensure_data_dir()
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(_SCHEMA)
        if self.get_meta("schema_version") is None:
            self.set_meta("schema_version", SCHEMA_VERSION)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # -- meta ---------------------------------------------------------------
    def get_meta(self, key: str) -> str | None:
        row = self.conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        self.conn.commit()

    # -- draws --------------------------------------------------------------
    def upsert_draw(self, draw: Draw) -> None:
        nums = sorted(draw.numbers)
        self.conn.execute(
            "INSERT INTO draws(draw_id, draw_date, n1,n2,n3,n4,n5,n6, extra, jackpot)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)"
            " ON CONFLICT(draw_id) DO UPDATE SET"
            " draw_date=excluded.draw_date, n1=excluded.n1, n2=excluded.n2,"
            " n3=excluded.n3, n4=excluded.n4, n5=excluded.n5, n6=excluded.n6,"
            " extra=excluded.extra, jackpot=excluded.jackpot",
            (draw.draw_id, draw.draw_date, *nums, draw.extra, draw.jackpot),
        )

    def upsert_draws(self, draws: list[Draw]) -> int:
        for d in draws:
            self.upsert_draw(d)
        self.conn.commit()
        return len(draws)

    def _row_to_draw(self, row: sqlite3.Row) -> Draw:
        return Draw(
            draw_id=row["draw_id"],
            draw_date=row["draw_date"],
            numbers=(row["n1"], row["n2"], row["n3"],
                     row["n4"], row["n5"], row["n6"]),
            extra=row["extra"],
            jackpot=row["jackpot"],
        )

    def all_draws(self) -> list[Draw]:
        """All draws, oldest first (by date then draw_id)."""
        rows = self.conn.execute(
            "SELECT * FROM draws ORDER BY draw_date ASC, draw_id ASC"
        ).fetchall()
        return [self._row_to_draw(r) for r in rows]

    def latest_draw(self) -> Draw | None:
        row = self.conn.execute(
            "SELECT * FROM draws ORDER BY draw_date DESC, draw_id DESC LIMIT 1"
        ).fetchone()
        return self._row_to_draw(row) if row else None

    def draws_page(self, page: int, page_size: int = 50) -> list[Draw]:
        offset = max(page, 0) * page_size
        rows = self.conn.execute(
            "SELECT * FROM draws ORDER BY draw_date DESC, draw_id DESC "
            "LIMIT ? OFFSET ?",
            (page_size, offset),
        ).fetchall()
        return [self._row_to_draw(r) for r in rows]

    def count_draws(self) -> int:
        return self.conn.execute("SELECT COUNT(*) AS c FROM draws").fetchone()["c"]

    def date_range(self) -> tuple[str | None, str | None]:
        row = self.conn.execute(
            "SELECT MIN(draw_date) AS lo, MAX(draw_date) AS hi FROM draws"
        ).fetchone()
        return (row["lo"], row["hi"]) if row else (None, None)

    # -- saved picks --------------------------------------------------------
    def save_pick(self, pick: Pick) -> int:
        created = pick.created_at or _now_iso()
        cur = self.conn.execute(
            "INSERT INTO saved_picks(created_at, numbers, method, note) "
            "VALUES(?,?,?,?)",
            (created, json.dumps(sorted(pick.numbers)), pick.method, pick.note or ""),
        )
        self.conn.commit()
        return cur.lastrowid

    def all_picks(self) -> list[Pick]:
        rows = self.conn.execute(
            "SELECT * FROM saved_picks ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [
            Pick(
                id=r["id"],
                created_at=r["created_at"],
                numbers=json.loads(r["numbers"]),
                method=r["method"],
                note=r["note"] or "",
            )
            for r in rows
        ]

    def delete_pick(self, pick_id: int) -> None:
        self.conn.execute("DELETE FROM saved_picks WHERE id = ?", (pick_id,))
        self.conn.commit()
