"""Nodo de preprocesamiento de texto."""

from src.agents.meeting.state import MeetingState


def preprocess_node(state: MeetingState) -> dict:
    """Normaliza raw_text (strip, mínima transformación)."""
    raw = state.get("raw_text", "") or ""
    return {"raw_text": raw.strip()}
