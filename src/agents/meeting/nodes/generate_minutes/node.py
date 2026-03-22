"""Nodo de generación de minuta formal."""

import os
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.agents.meeting.nodes.generate_minutes.prompt import GENERATE_MINUTES_PROMPT
from src.agents.meeting.state import MeetingState

EMPTY_MESSAGE = "Minuta: No se identificó información procesable en la reunión."
WORD_LIMIT = 150

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


def _truncate_to_word_limit(text: str, limit: int = WORD_LIMIT) -> str:
    """Trunca el texto a máximo `limit` palabras (split por espacios)."""
    if not text or not isinstance(text, str):
        return text
    words = text.split()
    if len(words) <= limit:
        return text
    # Buscar último punto o punto y coma antes del límite
    truncated = words[:limit]
    for i in range(len(truncated) - 1, -1, -1):
        if truncated[i].endswith(".") or truncated[i].endswith(";"):
            return " ".join(truncated[: i + 1])
    return " ".join(truncated)


def generate_minutes_node(state: MeetingState) -> dict:
    """Genera minuta formal a partir de participantes, temas y acciones."""
    participants = (state.get("participants") or "").strip()
    topics = (state.get("topics") or "").strip()
    actions = (state.get("actions") or "").strip()

    if _is_empty_input(participants, topics, actions):
        return {"minutes": EMPTY_MESSAGE}

    api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"minutes": EMPTY_MESSAGE}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt_text = GENERATE_MINUTES_PROMPT.format(
        participants=participants or "No identificados",
        topics=topics or "No hay temas identificados",
        actions=actions or "No hay acciones identificadas",
    )
    response = llm.invoke([HumanMessage(content=prompt_text)])
    content = response.content if hasattr(response, "content") else str(response)
    if not content:
        return {"minutes": EMPTY_MESSAGE}

    truncated = _truncate_to_word_limit(content)
    return {"minutes": truncated}
