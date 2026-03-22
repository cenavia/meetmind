"""Integración: persistencia tras POST /process y lectura GET /meetings."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.database import init_db, reset_db_engine


@pytest.fixture
def isolated_client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "meetings_test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    reset_db_engine()
    init_db()
    with TestClient(app) as client:
        yield client
    reset_db_engine()


def test_post_text_then_list_and_get(isolated_client: TestClient) -> None:
    body = {"text": "Reunión con Ana y Luis. Acordamos revisar el presupuesto."}
    pr = isolated_client.post("/api/v1/process/text", json=body)
    assert pr.status_code == 200
    pdata = pr.json()
    assert "meeting_id" in pdata
    assert pdata["meeting_id"] is not None

    lr = isolated_client.get("/api/v1/meetings")
    assert lr.status_code == 200
    items = lr.json()["items"]
    assert len(items) >= 1
    mid = items[0]["id"]
    assert pdata["meeting_id"] == mid

    gr = isolated_client.get(f"/api/v1/meetings/{mid}")
    assert gr.status_code == 200
    data = gr.json()
    assert data["id"] == mid
    assert "participants" in data
    assert data["status"] in ("completed", "partial")


def test_get_unknown_meeting_404(isolated_client: TestClient) -> None:
    r = isolated_client.get("/api/v1/meetings/00000000-0000-0000-0000-000000000099")
    assert r.status_code == 404
    assert "identificador" in r.json()["detail"].lower()


def test_list_five_ordered_desc(isolated_client: TestClient) -> None:
    for i in range(5):
        isolated_client.post(
            "/api/v1/process/text",
            json={"text": f"Reunión número {i}. Tema: seguimiento del punto {i}."},
        )
    lr = isolated_client.get("/api/v1/meetings")
    assert lr.status_code == 200
    items = lr.json()["items"]
    assert len(items) >= 5

    def _parse(ts: str) -> datetime:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)

    dts = [_parse(it["created_at"]) for it in items[:5]]
    assert all(dts[i] >= dts[i + 1] for i in range(len(dts) - 1))


def test_survives_engine_reset_same_file(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """SC-001: mismo fichero SQLite tras reset del motor (simula nuevo arranque)."""
    db_path = tmp_path / "survive.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    reset_db_engine()
    init_db()
    meeting_id: str
    with TestClient(app) as c1:
        r = c1.post(
            "/api/v1/process/text",
            json={"text": "Reunión de continuidad. Solo verificación de persistencia."},
        )
        assert r.status_code == 200
        items = c1.get("/api/v1/meetings").json()["items"]
        meeting_id = items[0]["id"]

    reset_db_engine()
    init_db()
    with TestClient(app) as c2:
        gr = c2.get(f"/api/v1/meetings/{meeting_id}")
        assert gr.status_code == 200
        assert gr.json()["id"] == meeting_id
