from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi.testclient import TestClient
import pytest

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    with TestClient(create_app(tmp_path / "weather.sqlite3")) as test_client:
        yield test_client


def payload(**overrides):
    return {
        "device_id": "esp32-01",
        "temperature_c": 24.3,
        "humidity_pct": 58.2,
        **overrides,
    }


def test_empty_database(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/readings").json() == []
    assert client.get("/api/readings/latest").status_code == 404


def test_create_reading_with_server_timestamp(client: TestClient):
    before = datetime.now(timezone.utc)
    response = client.post("/api/readings", json=payload())
    assert response.status_code == 201
    reading = response.json()
    assert reading["id"] == 1
    assert reading["measured_at"] is None
    received_at = datetime.fromisoformat(reading["received_at"].replace("Z", "+00:00"))
    assert before <= received_at <= datetime.now(timezone.utc)
    assert client.get("/api/readings/latest").json() == reading


def test_device_timestamp_is_normalized_to_utc(client: TestClient):
    response = client.post(
        "/api/readings", json=payload(measured_at="2026-10-24T12:00:00-03:00")
    )
    assert response.status_code == 201
    assert response.json()["measured_at"] == "2026-10-24T15:00:00Z"


@pytest.mark.parametrize(
    "changes",
    [
        {"device_id": " "},
        {"device_id": "x" * 65},
        {"temperature_c": -41},
        {"temperature_c": 81},
        {"humidity_pct": -1},
        {"humidity_pct": 101},
        {"temperature_c": "NaN"},
        {"humidity_pct": "Infinity"},
        {"measured_at": "2026-10-24T12:00:00"},
        {"received_at": "2026-10-24T12:00:00Z"},
    ],
)
def test_invalid_readings_are_rejected(client: TestClient, changes: dict[str, str] | dict[str, int]):
    assert client.post("/api/readings", json=payload(**changes)).status_code == 422
    assert client.get("/api/readings").json() == []


def test_filter_and_pagination(client: TestClient):
    for device_id in ["esp32-01", "esp32-02", "esp32-01"]:
        assert client.post("/api/readings", json=payload(device_id=device_id)).status_code == 201
    assert [r["id"] for r in client.get("/api/readings").json()] == [3, 2, 1]
    response = client.get("/api/readings", params={"device_id": "esp32-01", "limit": 1, "offset": 1})
    assert [r["id"] for r in response.json()] == [1]
    assert client.get("/api/readings/latest", params={"device_id": "esp32-02"}).json()["id"] == 2
    assert client.get("/api/readings/latest", params={"device_id": "unknown"}).status_code == 404


@pytest.mark.parametrize("query", ["limit=0", "limit=1001", "offset=-1"])
def test_invalid_pagination(client: TestClient, query: Literal['limit=0'] | Literal['limit=1001'] | Literal['offset=-1']):
    assert client.get(f"/api/readings?{query}").status_code == 422


def test_readings_persist_across_restarts(tmp_path: Path):
    database = tmp_path / "weather.sqlite3"
    with TestClient(create_app(database)) as first:
        assert first.post("/api/readings", json=payload()).status_code == 201
    with TestClient(create_app(database)) as second:
        assert second.get("/api/readings/latest").json()["device_id"] == "esp32-01"
