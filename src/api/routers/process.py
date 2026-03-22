"""Router de procesamiento de texto."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.agents.meeting.agent import get_graph
from src.api.dependencies import get_graph_dep
from src.services.file_loader import FileLoaderError, load_text_file

router = APIRouter(prefix="/process", tags=["process"])

MAX_TEXT_LENGTH = 50_000

ALLOWED_MIME_TYPES = {"text/plain", "text/markdown", "text/x-markdown"}


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


@router.post("/file", response_model=ProcessMeetingResponse)
async def process_file(
    file: Annotated[UploadFile, File(description="Archivo .txt o .md con notas de reunión")],
    graph=Depends(get_graph_dep),
) -> ProcessMeetingResponse:
    """Procesa archivo de texto (.txt o .md) y devuelve resultado estructurado."""
    if not file.filename:
        raise HTTPException(status_code=422, detail="El archivo debe tener nombre")

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Tipo de archivo no soportado. Solo text/plain y text/markdown.",
        )

    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {e}") from e

    try:
        text = load_text_file(content, file.filename)
    except FileLoaderError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e

    result = graph.invoke({"raw_text": text})

    return ProcessMeetingResponse(
        participants=result.get("participants", ""),
        topics=result.get("topics", ""),
        actions=result.get("actions", ""),
        minutes=result.get("minutes", ""),
        executive_summary=result.get("executive_summary", ""),
    )
