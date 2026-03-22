"""Nodo de extracción de participantes."""

import os
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.agents.meeting.nodes.extract_participants.prompt import EXTRACT_PARTICIPANTS_PROMPT
from src.agents.meeting.state import MeetingState


class ParticipantsExtraction(BaseModel):
    """Salida estructurada del LLM: lista de nombres de participantes."""

    participants: list[str]


def _sort_by_first_occurrence(names: list[str], raw_text: str) -> list[str]:
    """Ordena nombres por primera aparición en raw_text."""
    text_lower = raw_text.lower()
    result = []
    seen = set()

    def _find_pos(name: str) -> int:
        pos = text_lower.find(name.lower())
        return pos if pos >= 0 else 999_999

    for name in names:
        name_clean = name.strip()
        if not name_clean or name_clean.lower() in seen:
            continue
        seen.add(name_clean.lower())
        result.append(name_clean)

    return sorted(result, key=lambda n: _find_pos(n))


def extract_participants_node(state: MeetingState) -> dict:
    """Extrae nombres de participantes del texto usando LLM con salida estructurada."""
    raw_text = (state.get("raw_text") or "").strip()

    if not raw_text:
        return {"participants": "No identificados"}

    api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"participants": "No identificados"}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(ParticipantsExtraction)
    prompt_text = EXTRACT_PARTICIPANTS_PROMPT.format(raw_text=raw_text)
    extraction = structured_llm.invoke([HumanMessage(content=prompt_text)])

    names = extraction.participants if extraction else []
    if not names:
        return {"participants": "No identificados"}

    ordered = _sort_by_first_occurrence(names, raw_text)
    participants_str = ", ".join(ordered) if ordered else "No identificados"
    return {"participants": participants_str}
