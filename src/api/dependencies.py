"""Dependencias de FastAPI (inyección del grafo, etc.)."""

from src.agents.meeting.agent import get_graph


def get_graph_dep():
    """Retorna el grafo compilado para inyección en endpoints."""
    return get_graph()
