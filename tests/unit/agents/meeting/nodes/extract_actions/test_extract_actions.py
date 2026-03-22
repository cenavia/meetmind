"""Tests unitarios para el nodo extract_actions."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.meeting.nodes.extract_actions.node import (
    ActionItem,
    ActionsExtraction,
    extract_actions_node,
)


def test_extract_actions_empty_text_returns_no_acciones():
    """Texto vacío devuelve 'No hay acciones identificadas'."""
    result = extract_actions_node({"raw_text": ""})
    assert result["actions"] == "No hay acciones identificadas"


def test_extract_actions_whitespace_only_returns_no_acciones():
    """Texto solo con espacios devuelve 'No hay acciones identificadas'."""
    result = extract_actions_node({"raw_text": "   \n\t  "})
    assert result["actions"] == "No hay acciones identificadas"


@patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
def test_extract_actions_no_api_key_returns_no_acciones():
    """Sin OPENAI_API_KEY devuelve 'No hay acciones identificadas'."""
    result = extract_actions_node({
        "raw_text": "María enviará el informe antes del viernes."
    })
    assert result["actions"] == "No hay acciones identificadas"


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_explicit_responsible(mock_chat):
    """Texto 'María enviará el informe antes del viernes' → 'Enviar informe... | María'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Enviar informe antes del viernes", responsible="María")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "María enviará el informe antes del viernes."
        })

    assert "Enviar informe antes del viernes" in result["actions"]
    assert "María" in result["actions"]
    assert " | " in result["actions"]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_por_asignar_when_no_responsible(mock_chat):
    """Texto 'Se debe revisar el contrato' → 'Revisar el contrato | Por asignar'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Revisar el contrato", responsible="Por asignar")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "Se debe revisar el contrato."
        })

    assert "Revisar el contrato" in result["actions"]
    assert "Por asignar" in result["actions"]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_empty_list_returns_no_acciones(mock_chat):
    """LLM devuelve lista vacía → 'No hay acciones identificadas'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(actions=[])
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "Reunión de brainstorming sin acuerdos."
        })

    assert result["actions"] == "No hay acciones identificadas"


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_multiple_format_semicolon_separated(mock_chat):
    """Múltiples acciones: formato 'acción | responsable; acción2 | responsable2'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Enviar informe", responsible="María"),
            ActionItem(action="Revisar contrato", responsible="Juan"),
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "María enviará el informe. Juan revisará el contrato."
        })

    assert ";" in result["actions"]
    assert "Enviar informe" in result["actions"]
    assert "María" in result["actions"]
    assert "Revisar contrato" in result["actions"]
    assert "Juan" in result["actions"]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_first_responsible_when_multiple(mock_chat):
    """'María y Pedro se encargarán del informe' → primer responsable (María)."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Preparar informe", responsible="María")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "María y Pedro se encargarán del informe."
        })

    assert "María" in result["actions"]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_role_only_por_asignar(mock_chat):
    """'El gerente enviará el resumen' → responsable 'Por asignar'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Enviar resumen", responsible="Por asignar")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "El gerente enviará el resumen."
        })

    assert "Por asignar" in result["actions"]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_sanitizes_pipe_and_semicolon(mock_chat):
    """Acción o responsable con '|' o ';' se reformulan/sanitizan."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Revisar documento | versión final", responsible="Juan")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "Juan revisará el documento | versión final."
        })

    # El nodo sanitiza: | → ,  ; → ,
    assert " | " in result["actions"]
    parts = result["actions"].split(" | ")
    assert len(parts) == 2
    assert "|" not in parts[0] or "," in parts[0]


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_order_by_first_occurrence(mock_chat):
    """Acciones ordenadas por primera aparición en el texto."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Revisar contrato", responsible="Juan"),
            ActionItem(action="Enviar informe", responsible="María"),
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "María: Enviar informe. Juan: Revisar contrato."
        })

    # "Enviar informe" aparece antes que "Revisar contrato" en el texto
    assert "Enviar informe" in result["actions"]
    assert "Revisar contrato" in result["actions"]
    assert result["actions"].index("Enviar informe") < result["actions"].index("Revisar contrato")


@patch("src.agents.meeting.nodes.extract_actions.node.ChatOpenAI")
def test_extract_actions_empty_responsible_mapped_to_por_asignar(mock_chat):
    """LLM devuelve responsible vacío → se mapea a 'Por asignar'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ActionsExtraction(
        actions=[
            ActionItem(action="Revisar presupuesto", responsible="")
        ]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_actions_node({
            "raw_text": "Se debe revisar el presupuesto."
        })

    assert "Por asignar" in result["actions"]
