"""Tests de integración: executive_summary proviene de create_summary (no mock)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_text_executive_summary_in_response():
    """POST /process/text: response incluye executive_summary de create_summary."""
    response = client.post(
        "/api/v1/process/text",
        json={
            "text": "Reunión con Juan y María. Se discutió el presupuesto trimestral. "
            "María enviará el informe antes del viernes. Juan preparará la presentación."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "executive_summary" in data
    summary = data["executive_summary"]
    assert summary
    assert summary == "Resumen: No se identificó información procesable en la reunión." or (
        len(summary.split()) <= 30 and len(summary) > 10
    )


def test_process_text_executive_summary_always_present():
    """POST /process/text: executive_summary siempre presente y es string no vacío."""
    response = client.post(
        "/api/v1/process/text",
        json={
            "text": "Reunión de brainstorming. Se habló de ideas, innovación y presupuesto. Sin acuerdos concretos."
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "executive_summary" in data
    assert isinstance(data["executive_summary"], str)
    assert len(data["executive_summary"]) > 0
    assert data["executive_summary"] == "Resumen: No se identificó información procesable en la reunión." or (
        len(data["executive_summary"].split()) <= 30
    )
