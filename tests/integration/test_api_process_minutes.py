"""Tests de integración: minutes proviene de generate_minutes (no mock)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_text_minutes_in_response():
    """POST /process/text: response incluye minutes de generate_minutes."""
    response = client.post(
        "/api/v1/process/text",
        json={
            "text": "Reunión con Juan y María. Se discutió el presupuesto trimestral. "
            "María enviará el informe antes del viernes. Juan preparará la presentación."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "minutes" in data
    minutes = data["minutes"]
    assert minutes
    assert minutes == "Minuta: No se identificó información procesable en la reunión." or (
        len(minutes.split()) <= 150 and len(minutes) > 20
    )


def test_process_text_minutes_always_present():
    """POST /process/text: minutes siempre presente y es string no vacío (cuando hay datos)."""
    response = client.post(
        "/api/v1/process/text",
        json={
            "text": "Reunión de brainstorming. Se habló de ideas, innovación y presupuesto. Sin acuerdos concretos."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "minutes" in data
    assert isinstance(data["minutes"], str)
    assert len(data["minutes"]) > 0
    # Si hay datos extraídos → minuta generada; si no → mensaje fijo
    assert data["minutes"] == "Minuta: No se identificó información procesable en la reunión." or (
        len(data["minutes"].split()) <= 150
    )
