"""Estado del grafo de procesamiento de reuniones."""

import operator
from typing import Annotated

from typing_extensions import TypedDict


class MeetingState(TypedDict, total=False):
    """Estado compartido del grafo LangGraph."""

    raw_text: str
    """Texto de la reunión (entrada normalizada)."""

    transcript: str
    """Texto transcrito desde audio/vídeo cuando aplica; vacío si solo hubo texto."""

    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str
    processing_errors: Annotated[list[str], operator.add]
