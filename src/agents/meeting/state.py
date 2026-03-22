"""Estado del grafo de procesamiento de reuniones."""

from typing import TypedDict


class MeetingState(TypedDict, total=False):
    """Estado compartido del grafo LangGraph."""

    raw_text: str
    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str
