"""Tests unitarios para el nodo generate_minutes."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.meeting.nodes.generate_minutes.node import (
    EMPTY_MESSAGE,
    _is_empty_input,
    _truncate_to_word_limit,
    generate_minutes_node,
)


def test_is_empty_input_all_empty():
    """Todos vacíos → True."""
    assert _is_empty_input("", "", "") is True


def test_is_empty_input_no_identificados_literals():
    """Literales 'No identificados', 'No hay temas identificados', 'No hay acciones identificadas' → True."""
    assert _is_empty_input("No identificados", "No hay temas identificados", "No hay acciones identificadas") is True


def test_is_empty_input_partial_data_returns_false():
    """Solo temas → False."""
    assert _is_empty_input("No identificados", "Presupuesto; plazos", "No hay acciones identificadas") is False


def test_is_empty_input_full_data_returns_false():
    """Participantes, temas y acciones → False."""
    assert _is_empty_input("Juan, María", "Presupuesto", "Enviar informe | María") is False


def test_generate_minutes_empty_state_returns_fixed_message():
    """State vacío → minutes = mensaje fijo."""
    result = generate_minutes_node({
        "participants": "",
        "topics": "",
        "actions": "",
    })
    assert result["minutes"] == EMPTY_MESSAGE


def test_generate_minutes_all_no_data_literals_returns_fixed_message():
    """State con literales sin datos → minutes = mensaje fijo."""
    result = generate_minutes_node({
        "participants": "No identificados",
        "topics": "No hay temas identificados",
        "actions": "No hay acciones identificadas",
    })
    assert result["minutes"] == EMPTY_MESSAGE


@patch("src.agents.meeting.nodes.generate_minutes.node.ChatOpenAI")
def test_generate_minutes_empty_state_no_llm_call(mock_chat):
    """State vacío no invoca LLM."""
    generate_minutes_node({
        "participants": "",
        "topics": "",
        "actions": "",
    })
    mock_chat.assert_not_called()


@patch("src.agents.meeting.nodes.generate_minutes.node.ChatOpenAI")
def test_generate_minutes_with_data_invokes_llm(mock_chat):
    """State con datos invoca LLM y devuelve minuta."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Reunión con Juan y María. Se discutió el presupuesto."
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = generate_minutes_node({
            "participants": "Juan, María",
            "topics": "Presupuesto",
            "actions": "Enviar informe | María",
        })

    assert result["minutes"] == "Reunión con Juan y María. Se discutió el presupuesto."
    mock_llm.invoke.assert_called_once()


@patch("src.agents.meeting.nodes.generate_minutes.node.ChatOpenAI")
def test_generate_minutes_partial_data_integrates_topics_only(mock_chat):
    """State con solo temas → minuta integra lo disponible."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Reunión. Temas tratados: presupuesto y plazos."
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = generate_minutes_node({
            "participants": "No identificados",
            "topics": "Presupuesto; plazos",
            "actions": "No hay acciones identificadas",
        })

    assert "presupuesto" in result["minutes"].lower() or "plazos" in result["minutes"].lower()
    assert result["minutes"] != EMPTY_MESSAGE


def test_truncate_to_word_limit_under_limit_unchanged():
    """Texto ≤150 palabras no se trunca."""
    text = " ".join(["palabra"] * 100)
    assert _truncate_to_word_limit(text) == text


def test_truncate_to_word_limit_over_limit_truncates():
    """Texto >150 palabras se trunca."""
    text = " ".join(["palabra"] * 200)
    result = _truncate_to_word_limit(text)
    words = result.split()
    assert len(words) <= 150


def test_truncate_to_word_limit_preserves_sentence_boundary():
    """Truncamiento prioriza límite de oración cuando hay . o ;."""
    # Texto con punto en posición 5; limit 10
    text = "Una oración corta. " + " palabra" * 150
    result = _truncate_to_word_limit(text, limit=10)
    # Debe truncar en "corta." (posición 3) y devolver "Una oración corta."
    assert len(result.split()) <= 10
    # Si hay ., el resultado puede terminar en .
    assert result.endswith(".") or len(result.split()) == 10


def test_word_count_split_by_spaces():
    """Conteo de palabras usa split por espacios."""
    text = "palabra1 palabra2 palabra3"
    assert len(text.split()) == 3


@patch("src.agents.meeting.nodes.generate_minutes.node.ChatOpenAI")
def test_generate_minutes_llm_exceeds_150_words_truncates(mock_chat):
    """LLM devuelve >150 palabras → output ≤150."""
    long_text = " ".join(["palabra"] * 200)
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = long_text
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = generate_minutes_node({
            "participants": "Juan",
            "topics": "Tema",
            "actions": "Acción | Juan",
        })

    words = result["minutes"].split()
    assert len(words) <= 150


@patch("src.agents.meeting.nodes.generate_minutes.node.ChatOpenAI")
def test_generate_minutes_full_state_spanish_narrative(mock_chat):
    """State completo → minuta en español, narrativa, ≤150 palabras."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = (
        "Reunión con Juan y María. Se discutieron el presupuesto trimestral y los plazos. "
        "María enviará el informe antes del viernes. Juan preparará la presentación."
    )
    mock_llm.invoke.return_value = mock_response
    mock_chat.return_value = mock_llm

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        result = generate_minutes_node({
            "participants": "Juan, María",
            "topics": "Presupuesto; plazos",
            "actions": "Enviar informe | María; Preparar presentación | Juan",
        })

    assert len(result["minutes"].split()) <= 150
    assert "Juan" in result["minutes"] or "María" in result["minutes"]
    assert result["minutes"] != EMPTY_MESSAGE


@patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False)
def test_generate_minutes_no_api_key_returns_empty_message():
    """Sin OPENAI_API_KEY y con datos → mensaje fijo (fallback)."""
    result = generate_minutes_node({
        "participants": "Juan",
        "topics": "Tema",
        "actions": "Acción | Juan",
    })
    assert result["minutes"] == EMPTY_MESSAGE
