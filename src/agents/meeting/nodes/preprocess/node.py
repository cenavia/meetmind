"""Nodo de preprocesamiento de texto."""

from src.agents.meeting.state import MeetingState
from src.config import get_meeting_min_words


def preprocess_node(state: MeetingState) -> dict:
    """Normaliza raw_text (strip) y advierte si el texto es muy corto (spec 013)."""
    raw = state.get("raw_text", "") or ""
    stripped = raw.strip()
    words = stripped.split()
    min_w = get_meeting_min_words()
    if stripped and len(words) < min_w:
        return {
            "raw_text": stripped,
            "processing_errors": [
                f"El texto es muy corto (menos de {min_w} palabras). "
                "Los resultados pueden ser incompletos; considera añadir más contexto."
            ],
        }
    return {"raw_text": stripped}
