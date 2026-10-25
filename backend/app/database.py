"""SQLite initialization and reading persistence, independent of HTTP."""

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from .schemas import Reading, ReadingCreate


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect(database_path)) as connection, connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                measured_at TEXT,
                received_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_readings_device_id_id
                ON readings(device_id, id DESC);
            """
        )


def check_connection(database_path: Path) -> None:
    with closing(connect(database_path)) as connection:
        connection.execute("SELECT 1 FROM readings LIMIT 1").fetchone()


def insert_reading(database_path: Path, payload: ReadingCreate) -> Reading:
    received_at = datetime.now(timezone.utc)
    measured_at = (
        payload.measured_at.astimezone(timezone.utc)
        if payload.measured_at is not None
        else None
    )
    with closing(connect(database_path)) as connection, connection:
        cursor = connection.execute(
            """INSERT INTO readings
               (device_id, temperature_c, humidity_pct, measured_at, received_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                payload.device_id,
                payload.temperature_c,
                payload.humidity_pct,
                measured_at.isoformat() if measured_at else None,
                received_at.isoformat(),
            ),
        )
        reading_id = cursor.lastrowid
    return Reading(
        **payload.model_dump(exclude={"measured_at"}),
        measured_at=measured_at,
        received_at=received_at,
        id=reading_id,
    )


def get_latest_reading(
    database_path: Path, device_id: str | None = None,
) -> Reading | None:
    query = "SELECT * FROM readings"
    parameters = ()
    if device_id is not None:
        query += " WHERE device_id = ?"
        parameters = (device_id,)
    query += " ORDER BY id DESC LIMIT 1"
    with closing(connect(database_path)) as connection:
        row = connection.execute(query, parameters).fetchone()
    return Reading(**dict(row)) if row is not None else None


def get_readings(
    database_path: Path,
    device_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Reading]:
    query = "SELECT * FROM readings"
    parameters: list = []
    if device_id is not None:
        query += " WHERE device_id = ?"
        parameters.append(device_id)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    parameters.extend([limit, offset])
    with closing(connect(database_path)) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [Reading(**dict(row)) for row in rows]
