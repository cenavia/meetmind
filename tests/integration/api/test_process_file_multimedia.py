"""Tests de integración para process/file con multimedia."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


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
