"""Integración: liveness / readiness."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.database import init_db, reset_db_engine


@pytest.fixture
def isolated_client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "health_ready.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    reset_db_engine()
    init_db()
    with TestClient(app) as client:
        yield client
    reset_db_engine()


def test_health_ok_without_db_touch(isolated_client: TestClient) -> None:
    r = isolated_client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_ready_ok_when_db_up(isolated_client: TestClient) -> None:
    r = isolated_client.get("/ready")
    assert r.status_code == 200
    assert r.json().get("status") == "ready"


def test_ready_503_when_connectivity_check_fails(isolated_client: TestClient, monkeypatch) -> None:
    def boom() -> None:
        raise RuntimeError("simulated DB failure")

    monkeypatch.setattr("src.api.routers.health.check_database_connectivity", boom)
    r = isolated_client.get("/ready")
    assert r.status_code == 503
    assert "almacenamiento" in r.json()["detail"].lower()
