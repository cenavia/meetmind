"""Nodo mock que retorna datos hardcodeados según data-model.md."""

from src.agents.meeting.state import MeetingState


def mock_result_node(state: MeetingState) -> dict:
    """Retorna datos hardcodeados para validar el flujo E2E. No sobrescribe participants, topics, actions ni minutes (extraídos/generados por sus nodos)."""
    return {
        "executive_summary": "Acuerdo sobre presupuesto y plazos.",
    }
