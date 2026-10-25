"""Local-network API for weather station readings."""

from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ReadingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    device_id: str = Field(min_length=1, max_length=64)
    temperature_c: float = Field(ge=-40, le=80, allow_inf_nan=False)
    humidity_pct: float = Field(ge=0, le=100, allow_inf_nan=False)
    measured_at: AwareDatetime | None = None


class Reading(ReadingCreate):
    id: int
    received_at: AwareDatetime


def create_app(database_path: Path | None = None) -> FastAPI:
    db_path = Path(database_path) if database_path is not None else Path(
        os.environ.get(
            "WEATHER_DATABASE_PATH",
            str(Path(__file__).resolve().parents[1] / "data" / "weather.sqlite3"),
        )
    )

    def connect() -> sqlite3.Connection:
        connection = sqlite3.connect(db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(connect()) as connection, connection:
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
        yield

    app = FastAPI(title="ESP32 Weather Station API", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, str]:
        with closing(connect()) as connection:
            connection.execute("SELECT 1 FROM readings LIMIT 1").fetchone()
        return {"status": "ok"}

    @app.post("/api/readings", response_model=Reading, status_code=201)
    def create_reading(payload: ReadingCreate) -> Reading:
        received_at = datetime.now(timezone.utc)
        measured_at = (
            payload.measured_at.astimezone(timezone.utc)
            if payload.measured_at is not None
            else None
        )
        with closing(connect()) as connection, connection:
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

    @app.get("/api/readings/latest", response_model=Reading)
    def latest_reading(
        device_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
    ) -> Reading:
        query = "SELECT * FROM readings"
        parameters = ()
        if device_id is not None:
            query += " WHERE device_id = ?"
            parameters = (device_id,)
        query += " ORDER BY id DESC LIMIT 1"
        with closing(connect()) as connection:
            row = connection.execute(query, parameters).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="No readings found")
        return Reading(**dict(row))

    @app.get("/api/readings", response_model=list[Reading])
    def list_readings(
        device_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
        limit: Annotated[int, Query(ge=1, le=1000)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> list[Reading]:
        query = "SELECT * FROM readings"
        parameters: list = []
        if device_id is not None:
            query += " WHERE device_id = ?"
            parameters.append(device_id)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        parameters.extend([limit, offset])
        with closing(connect()) as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [Reading(**dict(row)) for row in rows]

    return app


app = create_app()
