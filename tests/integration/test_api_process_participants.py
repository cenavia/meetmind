"""Tests de integración: participants proviene de extract_participants (no mock)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_text_participants_from_extraction():
    """POST /process/text con texto con nombres: participants viene de extract_participants."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "Juan Pérez, María López y Pedro García asistieron. Juan propuso el tema."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    # Si hay OPENAI_API_KEY, participants debe ser extraído (nombres). Si no, "No identificados".
    participants = data["participants"]
    assert participants == "No identificados" or (
        "Juan" in participants or "María" in participants or "Pedro" in participants
    )


def test_process_text_no_names_returns_no_identificados():
    """POST /process/text sin nombres: participants = 'No identificados'."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "Se discutió el presupuesto. Hubo acuerdo sobre las fechas."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["participants"] == "No identificados"
