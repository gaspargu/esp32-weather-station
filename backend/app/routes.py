"""HTTP routes for health checks and sensor readings."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from . import database
from .schemas import Reading, ReadingCreate


def create_router(database_path: Path) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        database.check_connection(database_path)
        return {"status": "ok"}

    @router.post("/api/readings", response_model=Reading, status_code=201)
    def create_reading(payload: ReadingCreate) -> Reading:
        return database.insert_reading(database_path, payload)

    @router.get("/api/readings/latest", response_model=Reading)
    def latest_reading(
        device_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
    ) -> Reading:
        reading = database.get_latest_reading(database_path, device_id)
        if reading is None:
            raise HTTPException(status_code=404, detail="No readings found")
        return reading

    @router.get("/api/readings", response_model=list[Reading])
    def list_readings(
        device_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
        limit: Annotated[int, Query(ge=1, le=1000)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> list[Reading]:
        return database.get_readings(database_path, device_id, limit, offset)

    return router
