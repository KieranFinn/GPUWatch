"""SQLite time-series storage for GPU price data."""

from __future__ import annotations

import csv
import io
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

from src.config import DB_PATH
from src.models import GPUOffer

logger = logging.getLogger(__name__)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS gpu_prices (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    provider    TEXT NOT NULL,
    gpu_name    TEXT NOT NULL,
    gpu_memory  REAL NOT NULL,
    price_per_hour REAL NOT NULL,
    currency    TEXT NOT NULL DEFAULT 'USD',
    spot        INTEGER NOT NULL DEFAULT 0,
    region      TEXT NOT NULL DEFAULT '',
    timestamp   TEXT NOT NULL
);
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_gpu_prices_gpu_ts ON gpu_prices (gpu_name, timestamp);
"""


@contextmanager
def _connect(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    path = db_path or DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> None:
    """Create the database and tables if they don't exist."""
    with _connect(db_path) as conn:
        conn.execute(_CREATE_TABLE)
        conn.execute(_CREATE_INDEX)
    logger.info("Database initialised at %s", db_path or DB_PATH)


def save_snapshot(offers: list[GPUOffer], db_path: Optional[str] = None) -> int:
    """Persist a list of GPUOffer records. Returns number of rows inserted."""
    if not offers:
        return 0
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.executemany(
            """INSERT INTO gpu_prices
               (provider, gpu_name, gpu_memory, price_per_hour, currency, spot, region, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    o.provider,
                    o.gpu_name,
                    o.gpu_memory,
                    o.price_per_hour,
                    o.currency,
                    int(o.spot),
                    o.region,
                    o.timestamp.isoformat(),
                )
                for o in offers
            ],
        )
    logger.info("Saved %d offers to database", len(offers))
    return len(offers)


def get_latest(gpu_name: Optional[str] = None, db_path: Optional[str] = None) -> list[GPUOffer]:
    """Retrieve the most recent snapshot of prices.

    If *gpu_name* is given, filter to that GPU (case-insensitive LIKE).
    """
    init_db(db_path)
    with _connect(db_path) as conn:
        # Find the latest timestamp
        row = conn.execute("SELECT MAX(timestamp) AS ts FROM gpu_prices").fetchone()
        if row is None or row["ts"] is None:
            return []
        latest_ts = row["ts"]

        query = "SELECT * FROM gpu_prices WHERE timestamp = ?"
        params: list = [latest_ts]
        if gpu_name:
            query += " AND gpu_name LIKE ?"
            params.append(f"%{gpu_name}%")
        rows = conn.execute(query, params).fetchall()

    return [_row_to_offer(r) for r in rows]


def get_history(
    gpu_name: str,
    days: int = 30,
    db_path: Optional[str] = None,
) -> list[GPUOffer]:
    """Return price history for a GPU over the last *days* days."""
    init_db(db_path)
    from datetime import timedelta

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM gpu_prices WHERE gpu_name LIKE ? AND timestamp >= ? ORDER BY timestamp",
            (f"%{gpu_name}%", cutoff),
        ).fetchall()
    return [_row_to_offer(r) for r in rows]


def export_csv(output: Optional[str] = None, db_path: Optional[str] = None) -> str:
    """Export all data to CSV. Returns the CSV string (or writes to *output* path)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM gpu_prices ORDER BY timestamp, gpu_name").fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "provider", "gpu_name", "gpu_memory", "price_per_hour", "currency", "spot", "region", "timestamp"])
    for r in rows:
        writer.writerow([r["id"], r["provider"], r["gpu_name"], r["gpu_memory"], r["price_per_hour"], r["currency"], bool(r["spot"]), r["region"], r["timestamp"]])

    csv_text = buf.getvalue()
    if output:
        Path(output).write_text(csv_text)
        logger.info("Exported %d rows to %s", len(rows), output)
    return csv_text


def _row_to_offer(row: sqlite3.Row) -> GPUOffer:
    return GPUOffer(
        provider=row["provider"],
        gpu_name=row["gpu_name"],
        gpu_memory=row["gpu_memory"],
        price_per_hour=row["price_per_hour"],
        currency=row["currency"],
        spot=bool(row["spot"]),
        region=row["region"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
    )
