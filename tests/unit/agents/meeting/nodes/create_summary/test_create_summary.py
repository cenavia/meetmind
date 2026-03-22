"""Tests unitarios para el nodo create_summary."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.meeting.nodes.create_summary.node import (
    EMPTY_MESSAGE,
    _ensure_word_limit,
    _is_empty_input,
    _word_count,
    create_summary_node,
)


def test_is_empty_input_all_empty():
    """Todos vacíos → True."""
    assert _is_empty_input("", "", "") is True


def test_is_empty_input_no_identificados_literals():
    """Literales 'sin datos' → True."""
    assert _is_empty_input(
        "No identificados", "No hay temas identificados", "No hay acciones identificadas"
    ) is True


def test_is_empty_input_partial_data_returns_false():
    """Solo temas → False."""
    assert _is_empty_input(
        "No identificados", "Presupuesto; plazos", "No hay acciones identificadas"
    ) is False


def test_is_empty_input_full_data_returns_false():
    """Participantes, temas y acciones → False."""
    assert _is_empty_input("Juan, María", "Presupuesto", "Enviar informe | María") is False


def test_create_summary_empty_state_returns_fixed_message():
    """State vacío → executive_summary = mensaje fijo."""
    result = create_summary_node({
        "participants": "",
        "topics": "",
        "actions": "",
    })
    assert result["executive_summary"] == EMPTY_MESSAGE


def test_create_summary_all_no_data_literals_returns_fixed_message():
    """State con literales sin datos → executive_summary = mensaje fijo."""
    result = create_summary_node({
        "participants": "No identificados",
        "topics": "No hay temas identificados",
        "actions": "No hay acciones identificadas",
    })
    assert result["executive_summary"] == EMPTY_MESSAGE


@patch("src.agents.meeting.nodes.create_summary.node.ChatOpenAI")
def test_create_summary_empty_state_no_llm_call(mock_chat):
    """State vacío no invoca LLM."""
    create_summary_node({
        "participants": "",
        "topics": "",
        "actions": "",
    })
    mock_chat.assert_not_called()


def test_word_count_split_by_spaces():
    """Conteo de palabras usa split por espacios."""
    assert _word_count("palabra1 palabra2 palabra3") == 3
    assert _word_count("una dos tres cuatro") == 4


@patch("src.agents.meeting.nodes.create_summary.node.ChatOpenAI")
def test_create_summary_with_data_invokes_llm(mock_chat):
    """State con datos invoca LLM y devuelve resumen."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Acuerdo sobre presupuesto. María envía informe."
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = create_summary_node({
            "participants": "Juan, María",
            "topics": "Presupuesto",
            "actions": "Enviar informe | María",
            "minutes": "Reunión con Juan y María. Presupuesto acordado.",
        })

    assert result["executive_summary"] == "Acuerdo sobre presupuesto. María envía informe."
    assert _word_count(result["executive_summary"]) <= 30
    mock_llm.invoke.assert_called()


@patch("src.agents.meeting.nodes.create_summary.node.ChatOpenAI")
def test_create_summary_partial_data_informative_meeting(mock_chat):
    """State con solo temas (reunión informativa) → resumen sintetiza temas."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Reunión informativa. Temas: presupuesto, plazos."
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = create_summary_node({
            "participants": "No identificados",
            "topics": "Presupuesto; plazos",
            "actions": "No hay acciones identificadas",
            "minutes": "Reunión de seguimiento. Temas: presupuesto, plazos.",
        })

    assert "presupuesto" in result["executive_summary"].lower() or "plazos" in result["executive_summary"].lower()
    assert result["executive_summary"] != EMPTY_MESSAGE
    assert _word_count(result["executive_summary"]) <= 30


@patch("src.agents.meeting.nodes.create_summary.node.ChatOpenAI")
def test_create_summary_llm_exceeds_30_words_truncates_or_retries(mock_chat):
    """LLM devuelve >30 palabras → output ≤30."""
    long_text = " ".join(["palabra"] * 40)
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = long_text
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = create_summary_node({
            "participants": "Juan",
            "topics": "Tema",
            "actions": "Acción | Juan",
            "minutes": "Minuta corta.",
        })

    words = result["executive_summary"].split()
    assert len(words) <= 30


def test_ensure_word_limit_under_limit_unchanged():
    """Texto ≤30 palabras no se modifica."""
    mock_llm = MagicMock()
    text = " ".join(["palabra"] * 20)
    result = _ensure_word_limit(text, mock_llm)
    assert result == text
    mock_llm.invoke.assert_not_called()


def test_ensure_word_limit_over_limit_truncates_as_fallback():
    """Texto >30 palabras y retry falla → truncar."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = " ".join(["palabra"] * 35)
    mock_llm.invoke.return_value = mock_response

    long_text = " ".join(["palabra"] * 40)
    result = _ensure_word_limit(long_text, mock_llm, max_retries=2)

    assert _word_count(result) <= 30


@patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
def test_create_summary_no_api_key_returns_empty_message():
    """Sin OPENAI_API_KEY y con datos → mensaje fijo."""
    result = create_summary_node({
        "participants": "Juan",
        "topics": "Tema",
        "actions": "Acción | Juan",
        "minutes": "Minuta.",
    })
    assert result["executive_summary"] == EMPTY_MESSAGE
