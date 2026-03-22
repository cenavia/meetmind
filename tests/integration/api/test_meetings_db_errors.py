"""Integración: FR-014 — fallo de almacenamiento en listado/detalle → 503."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from src.api.dependencies import get_meeting_repository
from src.api.main import app
from src.db.database import init_db, reset_db_engine


class _FailingMeetingRepository:
    def list_all_by_created_desc(self):
        raise OperationalError("SELECT", {}, Exception("simulated"))

    def get_by_id(self, record_id: uuid.UUID):
        raise OperationalError("SELECT", {}, Exception("simulated"))


@pytest.fixture
def isolated_client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "meetings_err.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    reset_db_engine()
    init_db()
    with TestClient(app) as client:
        yield client
    reset_db_engine()
    app.dependency_overrides.clear()


def test_list_meetings_503_on_sqlalchemy_error(isolated_client: TestClient) -> None:
    app.dependency_overrides[get_meeting_repository] = lambda: _FailingMeetingRepository()
    try:
        r = isolated_client.get("/api/v1/meetings")
        assert r.status_code == 503
        assert "almacenamiento" in r.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_meeting_repository, None)


def test_get_meeting_503_on_sqlalchemy_error(isolated_client: TestClient) -> None:
    app.dependency_overrides[get_meeting_repository] = lambda: _FailingMeetingRepository()
    try:
        mid = uuid.UUID("00000000-0000-0000-0000-000000000001")
        r = isolated_client.get(f"/api/v1/meetings/{mid}")
        assert r.status_code == 503
        assert "almacenamiento" in r.json()["detail"].lower()
    finally:
        app.dependency_overrides.pop(get_meeting_repository, None)
