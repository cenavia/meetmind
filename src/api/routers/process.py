"""Router de procesamiento de texto y multimedia."""

import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Annotated
from uuid import UUID

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
router = APIRouter(
    prefix="/process",
    tags=["process"],
)

MAX_TEXT_LENGTH = 50_000

ALLOWED_MIME_TYPES_TEXT = {"text/plain", "text/markdown", "text/x-markdown"}


class ProcessTextRequest(BaseModel):
    """Request para procesar texto."""

    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH)


class ProcessMeetingResponse(BaseModel):
    """Response con resultado estructurado (spec 013: estado, avisos, transcripción)."""

    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str
    status: str
    processing_errors: list[str] = Field(default_factory=list)
    transcript: str = ""
    meeting_id: UUID | None = None


def _result_to_response(result: dict, meeting_id: UUID | None) -> ProcessMeetingResponse:
    from src.db.meeting_persist import public_process_fields

    d = public_process_fields(result, meeting_id)
    return ProcessMeetingResponse(
        participants=d["participants"],
        topics=d["topics"],
        actions=d["actions"],
        minutes=d["minutes"],
        executive_summary=d["executive_summary"],
        status=d["status"],
        processing_errors=d["processing_errors"],
        transcript=d["transcript"],
        meeting_id=meeting_id,
    )


def _persist_graph_success_or_503(
    repo: MeetingRepository,
    result: dict,
    *,
    source_file_name: str | None,
    source_file_type: str | None,
) -> UUID:
    try:
        row = persist_graph_success(
            repo,
            result,
            source_file_name=source_file_name,
            source_file_type=source_file_type,
        )
        return row.id
    except Exception:
        logger.exception("No se pudo persistir el resultado de la reunión")
        raise HTTPException(
            status_code=503,
            detail="No se pudo guardar el resultado en el almacenamiento. Intenta de nuevo más tarde.",
        ) from None


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


@router.post(
    "/text",
    response_model=ProcessMeetingResponse,
    summary="Procesar reunión desde texto",
    description=(
        "Envía el texto de la reunión en JSON; el procesamiento es **síncrono** hasta obtener "
        "participantes, temas, acciones, minuta y resumen. Incluye `status`, `processing_errors` "
        "(lista) y `transcript` (vacío si no hubo STT). Contrato: "
        "`specs/013-incomplete-error-feedback/contracts/processing-feedback.md`. "
        "Si la persistencia está activa, se crea un registro y se devuelve `meeting_id`."
    ),
    response_description="Resultado estructurado; puede incluir `meeting_id` si el guardado en BD tuvo éxito.",
)
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
    meeting_id = _persist_graph_success_or_503(
        repo,
        result,
        source_file_name=None,
        source_file_type=None,
    )

    return _result_to_response(result, meeting_id)


@router.post(
    "/file",
    response_model=ProcessMeetingResponse,
    summary="Procesar reunión desde archivo",
    description=(
        "Sube un archivo de texto (.txt, .md) o multimedia admitido; el servidor transcribe si aplica "
        "y ejecuta el análisis de forma **síncrona**. Respuesta alineada a `POST /text` "
        "(`status`, `processing_errors` como lista, `transcript` si hubo STT). Contrato: "
        "`specs/013-incomplete-error-feedback/contracts/processing-feedback.md`. "
        "`meeting_id` cuando la persistencia tiene éxito."
    ),
    response_description="Resultado estructurado; puede incluir `meeting_id` si el guardado en BD tuvo éxito.",
)
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
                return graph.invoke({"raw_text": text, "transcript": text})

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

        meeting_id = _persist_graph_success_or_503(
            repo,
            result,
            source_file_name=file.filename,
            source_file_type=content_type or ext,
        )
        return _result_to_response(result, meeting_id)

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
        meeting_id = _persist_graph_success_or_503(
            repo,
            result,
            source_file_name=file.filename,
            source_file_type=content_type or ext,
        )
        return _result_to_response(result, meeting_id)

    raise HTTPException(status_code=415, detail=MSG_FORMAT_UNSUPPORTED)


_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.post(
    "/file/stream",
    summary="Procesar archivo con progreso (SSE)",
    description="Igual que POST /file pero devuelve Server-Sent Events con fases y resultado final o error.",
)
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
    - `{"type":"complete","data":{...}}` (como ProcessMeetingResponse; puede incluir `meeting_id`)
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


@router.post(
    "/text/stream",
    summary="Procesar texto con progreso (SSE)",
    description="Procesamiento síncrono del grafo con eventos SSE (fase analyzing + complete o error).",
)
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
