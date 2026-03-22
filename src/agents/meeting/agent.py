"""Grafo LangGraph para procesamiento de reuniones."""

from langgraph.graph import END, StateGraph

from src.agents.meeting.nodes.mock_result.node import mock_result_node
from src.agents.meeting.nodes.preprocess.node import preprocess_node
from src.agents.meeting.state import MeetingState


def get_graph() -> StateGraph:
    """Construye y compila el grafo: preprocess → mock_result → END."""
    graph = StateGraph(MeetingState)

    graph.add_node("preprocess", preprocess_node)
    graph.add_node("mock_result", mock_result_node)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "mock_result")
    graph.add_edge("mock_result", END)

    return graph.compile()
