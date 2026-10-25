"""Application factory and lifecycle configuration."""

from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI

from . import database
from .routes import create_router


def create_app(database_path: Path | None = None) -> FastAPI:
    db_path = Path(database_path) if database_path is not None else Path(
        os.environ.get(
            "WEATHER_DATABASE_PATH",
            str(Path(__file__).resolve().parents[1] / "data" / "weather.sqlite3"),
        )
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database.initialize(db_path)
        yield

    app = FastAPI(title="ESP32 Weather Station API", lifespan=lifespan)
    app.include_router(create_router(db_path))
    return app


app = create_app()
