"""Tests de integración para process/file con multimedia."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.dependencies import get_graph_dep
from src.api.main import app

client = TestClient(app)


class _FakeGraph:
    def invoke(self, state: dict) -> dict:
        return {
            "participants": "P",
            "topics": "T",
            "actions": "A",
            "minutes": "M",
            "executive_summary": "E",
        }


@patch("src.api.routers.process.transcribe_audio")
def test_process_file_mp3_returns_structured_result(mock_transcribe):
    """POST /api/v1/process/file con MP3 válido devuelve resultado estructurado."""
    mock_transcribe.return_value = "Reunión de prueba con Marina y Pablo. Tema: planificación."
    content = b"\xff\xfb\x90\x00"  # Minimal MP3-like header (no válido para Whisper real)
    response = client.post(
        "/api/v1/process/file",
        files={"file": ("test.mp3", content, "audio/mpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    assert "topics" in data
    assert "actions" in data
    assert "minutes" in data
    assert "executive_summary" in data


@patch("src.api.process_file_stream.transcribe_audio")
def test_process_file_stream_mp3_sse(mock_transcribe):
    """POST /api/v1/process/file/stream devuelve SSE con fases y resultado final."""
    mock_transcribe.return_value = "Reunión de prueba."
    app.dependency_overrides[get_graph_dep] = lambda: _FakeGraph()
    try:
        content = b"\xff\xfb\x90\x00"
        with client.stream(
            "POST",
            "/api/v1/process/file/stream",
            files={"file": ("test.mp3", content, "audio/mpeg")},
        ) as response:
            assert response.status_code == 200
            raw = response.read().decode()
    finally:
        app.dependency_overrides.clear()

    assert "received" in raw
    assert "transcribing" in raw
    assert "analyzing" in raw
    assert "complete" in raw
    assert "participants" in raw
    assert "transcription_backend" in raw
