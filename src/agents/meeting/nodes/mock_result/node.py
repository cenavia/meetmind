"""Nodo mock que retorna datos hardcodeados según data-model.md."""

from src.agents.meeting.state import MeetingState


def mock_result_node(state: MeetingState) -> dict:
    """Retorna datos hardcodeados para validar el flujo E2E. No sobrescribe participants (viene de extract_participants)."""
    return {
        "topics": "Presupuesto; Fechas de entrega",
        "actions": "Revisar cifras|Juan | Enviar propuesta|María",
        "minutes": "Reunión de seguimiento. Se revisó el estado del presupuesto. "
        "Se acordó enviar propuesta actualizada antes del viernes.",
        "executive_summary": "Acuerdo sobre presupuesto y plazos.",
    }
