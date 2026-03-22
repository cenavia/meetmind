"""Router de procesamiento de texto y multimedia."""

import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from src.api.process_file_stream import stream_process_text_request, stream_process_uploaded_file
from src.api.dependencies import get_graph_dep, get_meeting_repository
from src.db.meeting_persist import persist_failed, persist_graph_success
from src.db.repository import MeetingRepository
from src.api.multimedia_validation import (
    MSG_FORMAT_UNSUPPORTED,
    get_extension_from_filename,
    is_multimedia_extension,
    validate_multimedia_file,
)
from src.config import get_processing_timeout_sec
from src.services.file_loader import FileLoaderError, load_text_file
from src.services.transcription import TranscriptionError, transcribe_audio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/process", tags=["process"])

MAX_TEXT_LENGTH = 50_000

ALLOWED_MIME_TYPES_TEXT = {"text/plain", "text/markdown", "text/x-markdown"}


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


def _try_persist_success(
    repo: MeetingRepository,
    result: dict,
    *,
    source_file_name: str | None,
    source_file_type: str | None,
) -> None:
    try:
        persist_graph_success(
            repo,
            result,
            source_file_name=source_file_name,
            source_file_type=source_file_type,
        )
    except Exception:
        logger.exception("No se pudo persistir el resultado de la reunión")


def _try_persist_failed(
    repo: MeetingRepository,
    message: str,
    *,
    source_file_name: str | None = None,
    source_file_type: str | None = None,
) -> None:
    try:
        persist_failed(
            repo,
            message,
            source_file_name=source_file_name,
            source_file_type=source_file_type,
        )
    except Exception:
        logger.exception("No se pudo persistir reunión en estado fallido")


@router.post("/text", response_model=ProcessMeetingResponse)
def process_text(
    body: ProcessTextRequest,
    graph=Depends(get_graph_dep),
    repo: MeetingRepository = Depends(get_meeting_repository),
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
    _try_persist_success(repo, result, source_file_name=None, source_file_type=None)

    return ProcessMeetingResponse(
        participants=result.get("participants", ""),
        topics=result.get("topics", ""),
        actions=result.get("actions", ""),
        minutes=result.get("minutes", ""),
        executive_summary=result.get("executive_summary", ""),
    )


@router.post("/file", response_model=ProcessMeetingResponse)
async def process_file(
    file: Annotated[
        UploadFile,
        File(description="Archivo .txt, .md o multimedia (MP4, MOV, MP3, WAV, M4A, WEBM, MKV)"),
    ],
    graph=Depends(get_graph_dep),
    repo: MeetingRepository = Depends(get_meeting_repository),
) -> ProcessMeetingResponse:
    """Procesa archivo de texto o multimedia y devuelve resultado estructurado."""
    if not file.filename:
        raise HTTPException(status_code=422, detail="El archivo debe tener nombre")

    try:
        content = await file.read()
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al leer el archivo. Intenta de nuevo.",
        ) from None

    ext = get_extension_from_filename(file.filename)
    content_type = (file.content_type or "").split(";")[0].strip().lower() if file.content_type else None

    if is_multimedia_extension(ext):
        err = validate_multimedia_file(ext, content_type, len(content))
        if err:
            if "supera" in err or "límite" in err:
                raise HTTPException(status_code=400, detail=err)
            raise HTTPException(status_code=415, detail=MSG_FORMAT_UNSUPPORTED)

        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        try:
            try:
                Path(tmp_path).write_bytes(content)
            except Exception:
                raise HTTPException(
                    status_code=500,
                    detail="Error al leer el archivo. Intenta de nuevo.",
                ) from None

            timeout_sec = get_processing_timeout_sec()

            def _transcribe_and_invoke():
                # Multimedia → texto solo con openai-whisper (ver src/services/transcription.py)
                text = transcribe_audio(tmp_path)
                return graph.invoke({"raw_text": text})

            try:
                with ThreadPoolExecutor(max_workers=1) as ex:
                    future = ex.submit(_transcribe_and_invoke)
                    result = future.result(timeout=timeout_sec)
            except FuturesTimeoutError:
                _try_persist_failed(
                    repo,
                    "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde.",
                    source_file_name=file.filename,
                    source_file_type=content_type or ext,
                )
                raise HTTPException(
                    status_code=408,
                    detail="El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde.",
                ) from None
            except TranscriptionError as e:
                detail = e.args[0] if e.args else "El formato del archivo no es compatible."
                logger.warning("Transcripción fallida para %s: %s", file.filename, detail)
                _try_persist_failed(
                    repo,
                    detail,
                    source_file_name=file.filename,
                    source_file_type=content_type or ext,
                )
                raise HTTPException(status_code=422, detail=detail) from e
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except OSError:
                pass
            try:
                os.close(fd)
            except OSError:
                pass

        _try_persist_success(
            repo,
            result,
            source_file_name=file.filename,
            source_file_type=content_type or ext,
        )
        return ProcessMeetingResponse(
            participants=result.get("participants", ""),
            topics=result.get("topics", ""),
            actions=result.get("actions", ""),
            minutes=result.get("minutes", ""),
            executive_summary=result.get("executive_summary", ""),
        )

    if ext in {".txt", ".md"}:
        if content_type and content_type not in ALLOWED_MIME_TYPES_TEXT:
            raise HTTPException(
                status_code=415,
                detail="Tipo de archivo no soportado. Solo text/plain y text/markdown.",
            )

        try:
            text = load_text_file(content, file.filename)
        except FileLoaderError as e:
            raise HTTPException(status_code=e.status_code, detail=e.message) from e

        result = graph.invoke({"raw_text": text})
        _try_persist_success(
            repo,
            result,
            source_file_name=file.filename,
            source_file_type=content_type or ext,
        )
        return ProcessMeetingResponse(
            participants=result.get("participants", ""),
            topics=result.get("topics", ""),
            actions=result.get("actions", ""),
            minutes=result.get("minutes", ""),
            executive_summary=result.get("executive_summary", ""),
        )

    raise HTTPException(status_code=415, detail=MSG_FORMAT_UNSUPPORTED)


_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.post("/file/stream")
async def process_file_stream(
    file: Annotated[
        UploadFile,
        File(description="Archivo .txt, .md o multimedia (streaming SSE con fases)"),
    ],
    graph=Depends(get_graph_dep),
    repo: MeetingRepository = Depends(get_meeting_repository),
):
    """
    Igual que POST /file pero devuelve **text/event-stream** (SSE).

    Eventos JSON en cada línea `data:`:
    - `{"type":"phase","phase":"received|transcribing|analyzing|text_loaded","message":"..."}`
    - `{"type":"complete","data":{...}}` (mismo shape que ProcessMeetingResponse)
    - `{"type":"error","status":4xx,"detail":"..."}`
    """
    content = await file.read()
    filename = file.filename or ""
    ct = file.content_type
    return StreamingResponse(
        stream_process_uploaded_file(content, filename, ct, graph, repo),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )


@router.post("/text/stream")
async def process_text_stream(
    body: ProcessTextRequest,
    graph=Depends(get_graph_dep),
    repo: MeetingRepository = Depends(get_meeting_repository),
):
    """Procesa texto con SSE (fase analyzing + complete o error)."""
    return StreamingResponse(
        stream_process_text_request(body.text, graph, repo),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )
