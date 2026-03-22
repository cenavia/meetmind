"""Router de procesamiento de texto."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.agents.meeting.agent import get_graph
from src.api.dependencies import get_graph_dep

router = APIRouter(prefix="/process", tags=["process"])

MAX_TEXT_LENGTH = 50_000


class ProcessTextRequest(BaseModel):
    """Request para procesar texto."""

    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH)


class ProcessMeetingResponse(BaseModel):
    """Response con resultado estructurado."""

    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str


@router.post("/text", response_model=ProcessMeetingResponse)
def process_text(
    body: ProcessTextRequest,
    graph=Depends(get_graph_dep),
) -> ProcessMeetingResponse:
    """Procesa texto de reunión y devuelve resultado estructurado."""
    text = body.text.strip()
    if not text:
        raise HTTPException(
            status_code=422,
            detail="El texto no puede estar vacío o contener solo espacios",
        )
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"El texto excede el límite de {MAX_TEXT_LENGTH} caracteres",
        )

    result = graph.invoke({"raw_text": text})

    return ProcessMeetingResponse(
        participants=result.get("participants", ""),
        topics=result.get("topics", ""),
        actions=result.get("actions", ""),
        minutes=result.get("minutes", ""),
        executive_summary=result.get("executive_summary", ""),
    )
