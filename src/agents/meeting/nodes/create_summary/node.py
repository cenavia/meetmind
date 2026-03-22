"""Nodo de generación de resumen ejecutivo."""

import os
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.agents.meeting.nodes.create_summary.prompt import (
    CREATE_SUMMARY_PROMPT,
    SHORTEN_PROMPT,
)
from src.agents.meeting.state import MeetingState

EMPTY_MESSAGE = "Resumen: No se identificó información procesable en la reunión."
WORD_LIMIT = 30
MAX_RETRIES = 2

_EMPTY_VALUES = frozenset({
    "",
    "no identificados",
    "no hay temas identificados",
    "no hay acciones identificadas",
})


def _is_empty_input(participants: str, topics: str, actions: str) -> bool:
    """Devuelve True si los tres campos están vacíos o son valores 'sin datos'."""
    def _is_empty(val: str) -> bool:
        if not val or not isinstance(val, str):
            return True
        return val.strip().lower() in _EMPTY_VALUES

    return _is_empty(participants) and _is_empty(topics) and _is_empty(actions)


def _word_count(text: str) -> int:
    """Cuenta palabras por split por espacios."""
    if not text or not isinstance(text, str):
        return 0
    return len(text.split())


def _truncate_to_word_limit(text: str, limit: int = WORD_LIMIT) -> str:
    """Trunca el texto a máximo `limit` palabras (split por espacios)."""
    if not text or not isinstance(text, str):
        return text
    words = text.split()
    if len(words) <= limit:
        return text
    truncated = words[:limit]
    for i in range(len(truncated) - 1, -1, -1):
        if truncated[i].endswith(".") or truncated[i].endswith(";"):
            return " ".join(truncated[: i + 1])
    return " ".join(truncated)


def _ensure_word_limit(
    text: str,
    llm: ChatOpenAI,
    limit: int = WORD_LIMIT,
    max_retries: int = MAX_RETRIES,
) -> str:
    """Si text excede limit palabras: retry con prompt de acortar (máx. max_retries); fallback truncar."""
    if _word_count(text) <= limit:
        return text

    for _ in range(max_retries):
        shorten_prompt = SHORTEN_PROMPT.format(text=text)
        response = llm.invoke([HumanMessage(content=shorten_prompt)])
        content = response.content if hasattr(response, "content") else str(response)
        if content and _word_count(content) <= limit:
            return content.strip()
        text = content or text

    return _truncate_to_word_limit(text, limit)


def create_summary_node(state: MeetingState) -> dict:
    """Genera resumen ejecutivo a partir de participantes, temas, acciones y minuta."""
    participants = (state.get("participants") or "").strip()
    topics = (state.get("topics") or "").strip()
    actions = (state.get("actions") or "").strip()
    minutes = (state.get("minutes") or "").strip()

    if _is_empty_input(participants, topics, actions):
        return {"executive_summary": EMPTY_MESSAGE}

    api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"executive_summary": EMPTY_MESSAGE}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt_text = CREATE_SUMMARY_PROMPT.format(
        participants=participants or "No identificados",
        topics=topics or "No hay temas identificados",
        actions=actions or "No hay acciones identificadas",
        minutes=minutes or "Sin minuta",
    )
    response = llm.invoke([HumanMessage(content=prompt_text)])
    content = response.content if hasattr(response, "content") else str(response)
    if not content:
        return {"executive_summary": EMPTY_MESSAGE}

    summary = _ensure_word_limit(content, llm)
    return {"executive_summary": summary}
