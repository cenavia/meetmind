"""Grafo LangGraph para procesamiento de reuniones."""

from langgraph.graph import END, StateGraph

from src.agents.meeting.nodes.extract_participants.node import extract_participants_node
from src.agents.meeting.nodes.identify_topics.node import identify_topics_node
from src.agents.meeting.nodes.mock_result.node import mock_result_node
from src.agents.meeting.nodes.preprocess.node import preprocess_node
from src.agents.meeting.state import MeetingState


def get_graph() -> StateGraph:
    """Construye y compila el grafo: preprocess → extract_participants → identify_topics → mock_result → END."""
    graph = StateGraph(MeetingState)

    graph.add_node("preprocess", preprocess_node)
    graph.add_node("extract_participants", extract_participants_node)
    graph.add_node("identify_topics", identify_topics_node)
    graph.add_node("mock_result", mock_result_node)

    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "extract_participants")
    graph.add_edge("extract_participants", "identify_topics")
    graph.add_edge("identify_topics", "mock_result")
    graph.add_edge("mock_result", END)

    return graph.compile()
