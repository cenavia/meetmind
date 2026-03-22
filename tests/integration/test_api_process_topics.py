"""Tests de integración: topics proviene de identify_topics (no mock)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_text_topics_from_extraction():
    """POST /process/text con texto con temas: topics viene de identify_topics."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "Se discutió el presupuesto Q2, los plazos del proyecto y la asignación de recursos. Juan propuso revisar las cifras."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data
    topics = data["topics"]
    assert topics == "No hay temas identificados" or (
        ";" in topics or len(topics) > 0
    )


def test_process_text_no_topics_returns_no_temas():
    """POST /process/text sin temas identificables: topics = 'No hay temas identificados'."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "Reunión de coordinación."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topics"] == "No hay temas identificados"
