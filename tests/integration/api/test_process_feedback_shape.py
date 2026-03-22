"""Forma de respuesta POST /process/text (spec 013)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.database import init_db, reset_db_engine


@pytest.fixture
def client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "fb_shape.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    reset_db_engine()
    init_db()
    # raise_server_exceptions=False: errores 500 devueltos como respuesta (no re-lanzan RuntimeError).
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    reset_db_engine()


def test_process_text_returns_status_and_errors_list(client: TestClient) -> None:
    r = client.post("/api/v1/process/text", json={"text": "corta"})
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["status"] in ("completed", "partial")
    assert "processing_errors" in data
    assert isinstance(data["processing_errors"], list)
    assert len(data["processing_errors"]) >= 1
    assert "transcript" in data
    assert data["transcript"] == ""


def test_unhandled_path_no_traceback_in_json(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from src.api.routers import process as process_mod

    def _boom(*_a, **_k):
        raise RuntimeError("SECRET_TRACE_XYZ should not appear in response")

    monkeypatch.setattr(process_mod, "_persist_graph_success_or_503", _boom)

    r = client.post(
        "/api/v1/process/text",
        json={"text": "Reunión larga " * 30},
    )
    assert r.status_code == 500
    body = r.json()
    assert "detail" in body
    assert "SECRET_TRACE_XYZ" not in str(body)
    assert "Traceback" not in str(body)
