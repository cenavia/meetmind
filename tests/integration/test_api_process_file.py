"""Tests de integración para POST /api/v1/process/file."""

import io

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_file_success_txt():
    """Archivo .txt válido retorna 200 y 5 salidas estructuradas."""
    content = b"Reuniones con Juan y Maria. Discutimos el presupuesto."
    files = {"file": ("notas.txt", io.BytesIO(content), "text/plain")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    assert "topics" in data
    assert "actions" in data
    assert "minutes" in data
    assert "executive_summary" in data


def test_process_file_success_md():
    """Archivo .md válido retorna 200."""
    content = b"# Reunion\n\nTemas: presupuesto."
    files = {"file": ("notas.md", io.BytesIO(content), "text/markdown")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 200


def test_process_file_empty_422():
    """Archivo vacío retorna 422."""
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 422
    assert "vacío" in response.json()["detail"].lower()


def test_process_file_whitespace_only_422():
    """Archivo con solo espacios retorna 422."""
    files = {"file": ("spaces.txt", io.BytesIO(b"   \n\t  "), "text/plain")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 422


def test_process_file_invalid_extension_400():
    """Archivo con extensión no permitida retorna 400 o 415."""
    content = b"content"
    files = {"file": ("doc.pdf", io.BytesIO(content), "application/pdf")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code in (400, 415)
    detail = response.json()["detail"].lower()
    assert "soportado" in detail or "txt" in detail or "md" in detail or "plain" in detail


def test_process_file_length_limit_400():
    """Contenido >50.000 caracteres retorna 400."""
    content = ("x" * 50_001).encode("utf-8")
    files = {"file": ("large.txt", io.BytesIO(content), "text/plain")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 400
    assert "50000" in response.json()["detail"]


def test_process_file_special_chars_utf8():
    """Caracteres especiales (ñ, á) se procesan correctamente."""
    content = "Reunión en Córdoba con José.".encode("utf-8")
    files = {"file": ("notas.txt", io.BytesIO(content), "text/plain")}
    response = client.post("/api/v1/process/file", files=files)
    assert response.status_code == 200
    data = response.json()
    # El resultado del mock debería incluir el texto procesado; verificamos que no hay error
    assert "participants" in data or "minutes" in data
