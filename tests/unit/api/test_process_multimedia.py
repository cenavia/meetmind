"""Tests unitarios para validación multimedia en process/file."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_file_rejects_avi_415():
    """Archivo .avi recibe 415 con mensaje de formatos permitidos."""
    response = client.post(
        "/api/v1/process/file",
        files={"file": ("test.avi", b"fake avi content", "video/x-msvideo")},
    )
    assert response.status_code == 415
    data = response.json()
    assert "detail" in data
    assert "MP4" in data["detail"] or "MOV" in data["detail"]
    assert "Formato no soportado" in data["detail"]


@patch("src.api.multimedia_validation.get_max_file_size_mb", return_value=1)
def test_process_file_rejects_oversize_multimedia_400(mock_max_mb):
    """Archivo multimedia > límite recibe 400."""
    oversized = b"x" * (2 * 1024 * 1024)  # 2 MB > 1 MB limit
    response = client.post(
        "/api/v1/process/file",
        files={"file": ("test.mp3", oversized, "audio/mpeg")},
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "límite" in data["detail"].lower() or "supera" in data["detail"].lower()
