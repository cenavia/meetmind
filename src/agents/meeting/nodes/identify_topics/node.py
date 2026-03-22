"""Nodo de identificación de temas principales."""

import os
from typing import Optional

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from src.agents.meeting.nodes.identify_topics.prompt import IDENTIFY_TOPICS_PROMPT
from src.agents.meeting.state import MeetingState


class TopicsExtraction(BaseModel):
    """Salida estructurada del LLM: lista de temas principales."""

    topics: list[str]


def _sort_by_first_occurrence(topics: list[str], raw_text: str) -> list[str]:
    """Ordena temas por primera aparición en raw_text."""
    text_lower = raw_text.lower()
    result = []
    seen = set()

    def _find_pos(topic: str) -> int:
        pos = text_lower.find(topic.lower())
        return pos if pos >= 0 else 999_999

    for topic in topics:
        topic_clean = topic.strip()
        if not topic_clean or topic_clean.lower() in seen:
            continue
        seen.add(topic_clean.lower())
        result.append(topic_clean)

    return sorted(result, key=lambda t: _find_pos(t))


def identify_topics_node(state: MeetingState) -> dict:
    """Identifica temas principales del texto usando LLM con salida estructurada."""
    raw_text = (state.get("raw_text") or "").strip()

    if not raw_text:
        return {"topics": "No hay temas identificados"}

    api_key: Optional[str] = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"topics": "No hay temas identificados"}

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(TopicsExtraction)
    prompt_text = IDENTIFY_TOPICS_PROMPT.format(raw_text=raw_text)
    extraction = structured_llm.invoke([HumanMessage(content=prompt_text)])

    topics_list = extraction.topics if extraction else []
    if not topics_list:
        return {"topics": "No hay temas identificados"}

    ordered = _sort_by_first_occurrence(topics_list, raw_text)
    topics_str = "; ".join(ordered) if ordered else "No hay temas identificados"
    return {"topics": topics_str}
