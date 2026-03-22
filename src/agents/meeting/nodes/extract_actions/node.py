"""Nodo de extracción de acciones acordadas con responsables."""

import os
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.agents.meeting.nodes.extract_actions.prompt import EXTRACT_ACTIONS_PROMPT
from src.agents.meeting.state import MeetingState


class ActionItem(BaseModel):
    """Par acción-responsable."""

    action: str
    responsible: str


class ActionsExtraction(BaseModel):
    """Salida estructurada del LLM: lista de pares acción-responsable."""

    actions: list[ActionItem]


def _sanitize_for_format(text: str) -> str:
    """Reemplaza | y ; para evitar romper el formato de salida."""
    if not text or not isinstance(text, str):
        return text
    return text.replace("|", ",").replace(";", ",").strip()


def _sort_by_first_occurrence(items: list[ActionItem], raw_text: str) -> list[ActionItem]:
    """Ordena por primera aparición de la acción en raw_text."""
    text_lower = raw_text.lower()

    def _find_pos(action: str) -> int:
        pos = text_lower.find(action.lower())
        return pos if pos >= 0 else 999_999

    return sorted(items, key=lambda x: _find_pos(x.action))


def extract_actions_node(state: MeetingState) -> dict:
    """Extrae acciones acordadas con responsable usando LLM con salida estructurada."""
    raw_text = (state.get("raw_text") or "").strip()

    if not raw_text:
        return {"actions": "No hay acciones identificadas"}

    api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"actions": "No hay acciones identificadas"}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(ActionsExtraction)
    prompt_text = EXTRACT_ACTIONS_PROMPT.format(raw_text=raw_text)
    extraction = structured_llm.invoke([HumanMessage(content=prompt_text)])

    items = extraction.actions if extraction else []
    if not items:
        return {"actions": "No hay acciones identificadas"}

    for item in items:
        item.action = _sanitize_for_format(item.action)
        item.responsible = _sanitize_for_format(item.responsible) or "Por asignar"
        if not item.responsible or item.responsible.isspace():
            item.responsible = "Por asignar"

    ordered = _sort_by_first_occurrence(items, raw_text)
    parts = [f"{a.action} | {a.responsible}" for a in ordered]
    actions_str = "; ".join(parts) if parts else "No hay acciones identificadas"
    return {"actions": actions_str}
