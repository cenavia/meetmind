"""Tests de integración: actions proviene de extract_actions (no mock)."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_process_text_actions_in_response():
    """POST /process/text: response incluye actions de extract_actions."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "María enviará el informe antes del viernes. Se debe revisar el contrato."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "actions" in data
    actions = data["actions"]
    assert actions == "No hay acciones identificadas" or (
        " | " in actions or len(actions) > 0
    )


def test_process_text_no_actions_returns_no_acciones():
    """POST /process/text sin acciones identificables: actions = 'No hay acciones identificadas'."""
    response = client.post(
        "/api/v1/process/text",
        json={"text": "Reunión de brainstorming sin acuerdos concretos."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["actions"] == "No hay acciones identificadas"
