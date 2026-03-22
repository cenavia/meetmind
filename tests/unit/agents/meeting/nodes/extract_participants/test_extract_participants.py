"""Tests unitarios para el nodo extract_participants."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.meeting.nodes.extract_participants.node import (
    ParticipantsExtraction,
    extract_participants_node,
)


def test_extract_participants_empty_text_returns_no_identificados():
    """Texto vacío devuelve 'No identificados'."""
    result = extract_participants_node({"raw_text": ""})
    assert result["participants"] == "No identificados"


def test_extract_participants_whitespace_only_returns_no_identificados():
    """Texto solo con espacios devuelve 'No identificados'."""
    result = extract_participants_node({"raw_text": "   \n\t  "})
    assert result["participants"] == "No identificados"


@patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
def test_extract_participants_no_api_key_returns_no_identificados():
    """Sin OPENAI_API_KEY devuelve 'No identificados'."""
    result = extract_participants_node({
        "raw_text": "Juan, María y Pedro asistieron a la reunión."
    })
    assert result["participants"] == "No identificados"


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_with_names_returns_comma_separated(mock_chat):
    """Texto con nombres devuelve lista separada por comas."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(
        participants=["Juan", "María", "Pedro"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "Juan, María y Pedro asistieron a la reunión."
        })

    assert result["participants"] == "Juan, María, Pedro"


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_empty_list_returns_no_identificados(mock_chat):
    """LLM devuelve lista vacía → 'No identificados'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(participants=[])
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "Se discutió el presupuesto. Hubo acuerdo."
        })

    assert result["participants"] == "No identificados"


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_dedup_prefers_full_name(mock_chat):
    """Variantes de mismo nombre: una entrada, preferir nombre completo."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(
        participants=["Laura García"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "Laura García propuso... Laura acordó..."
        })

    assert "Laura García" in result["participants"]
    assert result["participants"].count("Laura") == 1


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_order_by_first_occurrence(mock_chat):
    """Nombres ordenados por primera aparición en el texto."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(
        participants=["Pedro", "Juan", "María"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "María abrió la reunión. Juan propuso. Pedro cerró."
        })

    assert result["participants"] == "María, Juan, Pedro"


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_excludes_titles(mock_chat):
    """Nombres sin títulos (Dr., Ing., etc.)."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(
        participants=["García", "López"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "El Dr. García y la Ing. López asistieron."
        })

    assert "Dr." not in result["participants"]
    assert "Ing." not in result["participants"]
    assert "García" in result["participants"] or "López" in result["participants"]


@patch("src.agents.meeting.nodes.extract_participants.node.ChatOpenAI")
def test_extract_participants_excludes_generic_terms(mock_chat):
    """No incluye 'persona' ni 'alguien'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = ParticipantsExtraction(
        participants=["Juan", "María"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = extract_participants_node({
            "raw_text": "Juan, María y una persona asistieron. Alguien preguntó."
        })

    assert "persona" not in result["participants"].lower()
    assert "alguien" not in result["participants"].lower()
    assert "Juan" in result["participants"]
    assert "María" in result["participants"]
