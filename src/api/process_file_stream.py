"""Streaming SSE para procesamiento de archivos y texto (fases reales en servidor)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from uuid import UUID

from starlette.concurrency import run_in_threadpool

from src.api.multimedia_validation import (
    MSG_FORMAT_UNSUPPORTED,
    get_extension_from_filename,
    is_multimedia_extension,
    validate_multimedia_file,
)
from src.config import get_processing_timeout_sec, get_transcription_backend
from src.db.meeting_persist import persist_failed, persist_graph_success
from src.db.repository import MeetingRepository
from src.services.file_loader import FileLoaderError, load_text_file
from src.services.transcription import TranscriptionError, transcribe_audio

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES_TEXT = {"text/plain", "text/markdown", "text/x-markdown"}
MAX_TEXT_LENGTH = 50_000


def sse_event(data: dict) -> str:
    """Un evento Server-Sent Events (una línea data: JSON + líneas en blanco)."""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _response_dict(result: dict, meeting_id: UUID | None = None) -> dict:
    out = {
        "participants": result.get("participants", ""),
        "topics": result.get("topics", ""),
        "actions": result.get("actions", ""),
        "minutes": result.get("minutes", ""),
        "executive_summary": result.get("executive_summary", ""),
    }
    if meeting_id is not None:
        out["meeting_id"] = str(meeting_id)
    return out


def _sse_persist_graph_success(
    repo: MeetingRepository,
    result: dict,
    *,
    source_file_name: str | None,
    source_file_type: str | None,
) -> UUID | None:
    try:
        row = persist_graph_success(
            repo,
            result,
            source_file_name=source_file_name,
            source_file_type=source_file_type,
        )
        return row.id
    except Exception:
        logger.exception("No se pudo persistir el resultado de la reunión (SSE)")
        return None


def _sse_try_persist_failed(
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
        logger.exception("No se pudo persistir reunión fallida (SSE)")


async def stream_process_uploaded_file(
    content: bytes,
    filename: str,
    content_type: str | None,
    graph: Any,
    repo: MeetingRepository,
) -> AsyncIterator[str]:
    """Generador async de fragmentos SSE para un archivo ya leído en memoria."""
    if not filename:
        yield sse_event({"type": "error", "status": 422, "detail": "El archivo debe tener nombre"})
        return

    ext = get_extension_from_filename(filename)
    ct = (content_type or "").split(";")[0].strip().lower() if content_type else None
    timeout_sec = get_processing_timeout_sec()
    deadline = time.monotonic() + timeout_sec

    def remaining() -> float:
        return max(1.0, deadline - time.monotonic())

    if is_multimedia_extension(ext):
        whisper_mode = get_transcription_backend()
        err = validate_multimedia_file(ext, ct, len(content))
        if err:
            code = 400 if ("supera" in err or "límite" in err) else 415
            yield sse_event({"type": "error", "status": code, "detail": err})
            return

        yield sse_event(
            {
                "type": "phase",
                "phase": "received",
                "message": "Archivo recibido en el servidor; preparando transcripción.",
                "transcription_backend": whisper_mode,
            }
        )

        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        try:
            try:
                os.write(fd, content)
            finally:
                os.close(fd)
        except OSError:
            Path(tmp_path).unlink(missing_ok=True)
            yield sse_event(
                {"type": "error", "status": 500, "detail": "Error al guardar el archivo temporal."}
            )
            return

        try:
            yield sse_event(
                {
                    "type": "phase",
                    "phase": "transcribing",
                    "message": (
                        "Transcripción con Whisper en la nube (OpenAI)…"
                        if whisper_mode == "cloud"
                        else "Transcripción con Whisper local en el servidor…"
                    ),
                    "transcription_backend": whisper_mode,
                }
            )
            try:
                text = await asyncio.wait_for(
                    run_in_threadpool(transcribe_audio, tmp_path),
                    timeout=remaining(),
                )
            except TranscriptionError as e:
                detail = e.args[0] if e.args else "El formato del archivo no es compatible."
                logger.warning("Transcripción fallida para %s: %s", filename, detail)
                _sse_try_persist_failed(
                    repo,
                    detail,
                    source_file_name=filename,
                    source_file_type=ct or ext,
                )
                yield sse_event({"type": "error", "status": 422, "detail": detail})
                return
            except TimeoutError:
                msg = "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde."
                _sse_try_persist_failed(
                    repo,
                    msg,
                    source_file_name=filename,
                    source_file_type=ct or ext,
                )
                yield sse_event(
                    {
                        "type": "error",
                        "status": 408,
                        "detail": msg,
                    }
                )
                return

            yield sse_event(
                {
                    "type": "phase",
                    "phase": "analyzing",
                    "message": "Analizando la reunión (participantes, temas, minuta, resumen)…",
                    "transcription_backend": whisper_mode,
                }
            )

            def _invoke_graph() -> dict:
                return graph.invoke({"raw_text": text})

            try:
                result = await asyncio.wait_for(
                    run_in_threadpool(_invoke_graph),
                    timeout=remaining(),
                )
            except TimeoutError:
                msg = "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde."
                _sse_try_persist_failed(
                    repo,
                    msg,
                    source_file_name=filename,
                    source_file_type=ct or ext,
                )
                yield sse_event(
                    {
                        "type": "error",
                        "status": 408,
                        "detail": msg,
                    }
                )
                return

            meeting_id = _sse_persist_graph_success(
                repo,
                result,
                source_file_name=filename,
                source_file_type=ct or ext,
            )
            if meeting_id is None:
                yield sse_event(
                    {
                        "type": "error",
                        "status": 503,
                        "detail": "No se pudo guardar el resultado en el almacenamiento. Intenta de nuevo más tarde.",
                    }
                )
                return
            yield sse_event({"type": "complete", "data": _response_dict(result, meeting_id)})
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        return

    if ext in {".txt", ".md"}:
        if ct and ct not in ALLOWED_MIME_TYPES_TEXT:
            yield sse_event(
                {
                    "type": "error",
                    "status": 415,
                    "detail": "Tipo de archivo no soportado. Solo text/plain y text/markdown.",
                }
            )
            return

        yield sse_event(
            {
                "type": "phase",
                "phase": "received",
                "message": "Archivo de texto recibido.",
                "transcription_backend": "none",
            }
        )

        try:
            text = await run_in_threadpool(load_text_file, content, filename)
        except FileLoaderError as e:
            yield sse_event({"type": "error", "status": e.status_code, "detail": e.message})
            return

        yield sse_event(
            {
                "type": "phase",
                "phase": "text_loaded",
                "message": "Texto extraído; iniciando análisis con IA.",
                "transcription_backend": "none",
            }
        )

        def _invoke_txt() -> dict:
            return graph.invoke({"raw_text": text})

        try:
            result = await asyncio.wait_for(
                run_in_threadpool(_invoke_txt),
                timeout=remaining(),
            )
        except TimeoutError:
            msg = "El procesamiento tardó demasiado. Intenta de nuevo."
            _sse_try_persist_failed(
                repo,
                msg,
                source_file_name=filename,
                source_file_type=ct or ext,
            )
            yield sse_event(
                {
                    "type": "error",
                    "status": 408,
                    "detail": msg,
                }
            )
            return

        meeting_id = _sse_persist_graph_success(
            repo,
            result,
            source_file_name=filename,
            source_file_type=ct or ext,
        )
        if meeting_id is None:
            yield sse_event(
                {
                    "type": "error",
                    "status": 503,
                    "detail": "No se pudo guardar el resultado en el almacenamiento. Intenta de nuevo más tarde.",
                }
            )
            return
        yield sse_event({"type": "complete", "data": _response_dict(result, meeting_id)})
        return

    yield sse_event({"type": "error", "status": 415, "detail": MSG_FORMAT_UNSUPPORTED})


async def stream_process_text_request(raw_text: str, graph: Any, repo: MeetingRepository) -> AsyncIterator[str]:
    """SSE para POST /text/stream (cuerpo ya validado como string)."""
    text = raw_text.strip()
    if not text:
        yield sse_event(
            {
                "type": "error",
                "status": 422,
                "detail": "El texto no puede estar vacío o contener solo espacios",
            }
        )
        return
    if len(text) > MAX_TEXT_LENGTH:
        yield sse_event(
            {
                "type": "error",
                "status": 400,
                "detail": f"El texto excede el límite de {MAX_TEXT_LENGTH} caracteres",
            }
        )
        return

    timeout_sec = get_processing_timeout_sec()
    deadline = time.monotonic() + timeout_sec

    def remaining() -> float:
        return max(1.0, deadline - time.monotonic())

    yield sse_event(
        {
            "type": "phase",
            "phase": "analyzing",
            "message": "Analizando la reunión con IA…",
            "transcription_backend": "none",
        }
    )

    def _invoke() -> dict:
        return graph.invoke({"raw_text": text})

    try:
        result = await asyncio.wait_for(
            run_in_threadpool(_invoke),
            timeout=remaining(),
        )
    except TimeoutError:
        msg = "El procesamiento tardó demasiado. Intenta de nuevo o usa un texto más corto."
        _sse_try_persist_failed(repo, msg, source_file_name=None, source_file_type=None)
        yield sse_event(
            {
                "type": "error",
                "status": 408,
                "detail": msg,
            }
        )
        return

    meeting_id = _sse_persist_graph_success(
        repo, result, source_file_name=None, source_file_type=None
    )
    if meeting_id is None:
        yield sse_event(
            {
                "type": "error",
                "status": 503,
                "detail": "No se pudo guardar el resultado en el almacenamiento. Intenta de nuevo más tarde.",
            }
        )
        return
    yield sse_event({"type": "complete", "data": _response_dict(result, meeting_id)})
