"""Tests unitarios para el nodo identify_topics."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.meeting.nodes.identify_topics.node import (
    TopicsExtraction,
    identify_topics_node,
)


def test_identify_topics_empty_text_returns_no_temas():
    """Texto vacío devuelve 'No hay temas identificados'."""
    result = identify_topics_node({"raw_text": ""})
    assert result["topics"] == "No hay temas identificados"


def test_identify_topics_whitespace_only_returns_no_temas():
    """Texto solo con espacios devuelve 'No hay temas identificados'."""
    result = identify_topics_node({"raw_text": "   \n\t  "})
    assert result["topics"] == "No hay temas identificados"


@patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
def test_identify_topics_no_api_key_returns_no_temas():
    """Sin OPENAI_API_KEY devuelve 'No hay temas identificados'."""
    result = identify_topics_node({
        "raw_text": "Se discutió presupuesto, plazos y recursos."
    })
    assert result["topics"] == "No hay temas identificados"


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_with_topics_returns_semicolon_separated(mock_chat):
    """Texto con temas devuelve lista separada por punto y coma."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(
        topics=["Presupuesto", "Plazos", "Recursos"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Se discutió el presupuesto, plazos y recursos."
        })

    assert result["topics"] == "Presupuesto; Plazos; Recursos"


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_empty_list_returns_no_temas(mock_chat):
    """LLM devuelve lista vacía → 'No hay temas identificados'."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(topics=[])
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Reunión de coordinación."
        })

    assert result["topics"] == "No hay temas identificados"


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_two_topics_no_filler(mock_chat):
    """Texto con 2 temas: exactamente 2, sin inventar."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(
        topics=["Presupuesto", "Plazos"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Se habló de presupuesto y plazos."
        })

    parts = result["topics"].split("; ")
    assert len(parts) == 2
    assert "Presupuesto" in result["topics"]
    assert "Plazos" in result["topics"]


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_overlapping_consolidated(mock_chat):
    """Temas solapados se consolidan (variante más específica)."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(
        topics=["Presupuesto Q2"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Se discutió el presupuesto. El Presupuesto Q2 fue clave."
        })

    assert "Presupuesto Q2" in result["topics"]
    assert result["topics"].count("Presupuesto") <= 2


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_avoids_generic_topics(mock_chat):
    """Evita 'Reunión de trabajo'; incluye temas específicos."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(
        topics=["Sprint 12", "Módulo de facturación"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Revisión del sprint 12 y bugs del módulo de facturación."
        })

    assert "Reunión de trabajo" not in result["topics"]
    assert "Sprint 12" in result["topics"] or "Módulo de facturación" in result["topics"]


@patch("src.agents.meeting.nodes.identify_topics.node.ChatOpenAI")
def test_identify_topics_order_by_first_occurrence(mock_chat):
    """Temas ordenados por primera aparición en el texto."""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TopicsExtraction(
        topics=["Recursos", "Presupuesto", "Plazos"]
    )
    mock_llm.with_structured_output.return_value = mock_structured
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = identify_topics_node({
            "raw_text": "Presupuesto primero. Plazos después. Recursos al final."
        })

    assert result["topics"] == "Presupuesto; Plazos; Recursos"
