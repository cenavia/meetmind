"""Reglas de persistencia tras procesamiento (capa API)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from src.db.models import MeetingRecord
from src.db.processing_errors_codec import decode_processing_errors, encode_processing_errors
from src.db.repository import MeetingRepository

LIMITED_PREFIX = "[Información limitada]"


def errors_list_from_graph_result(result: dict[str, Any]) -> list[str]:
    """Normaliza `processing_errors` del dict del grafo a lista de strings."""
    pe = result.get("processing_errors")
    if pe is None:
        return []
    if isinstance(pe, list):
        return [str(x).strip() for x in pe if str(x).strip()]
    if isinstance(pe, str) and pe.strip():
        return [pe.strip()]
    return []


def status_from_graph_result(result: dict[str, Any]) -> str:
    """Deriva completed vs partial según errores y prefijos de salida limitada."""
    if errors_list_from_graph_result(result):
        return "partial"
    minutes = (result.get("minutes") or "").strip()
    summary = (result.get("executive_summary") or "").strip()
    if minutes.startswith(LIMITED_PREFIX) or summary.startswith(LIMITED_PREFIX):
        return "partial"
    return "completed"


def public_process_fields(result: dict[str, Any], meeting_id: UUID | None) -> dict[str, Any]:
    """
    Cuerpo JSON alineado a spec 013 / contrato processing-feedback (SSE y referencia DTO).
    """
    out: dict[str, Any] = {
        "participants": result.get("participants", ""),
        "topics": result.get("topics", ""),
        "actions": result.get("actions", ""),
        "minutes": result.get("minutes", ""),
        "executive_summary": result.get("executive_summary", ""),
        "status": status_from_graph_result(result),
        "processing_errors": errors_list_from_graph_result(result),
        "transcript": (result.get("transcript") or "").strip(),
    }
    if meeting_id is not None:
        out["meeting_id"] = str(meeting_id)
    return out


def persist_graph_success(
    repo: MeetingRepository,
    result: dict[str, Any],
    *,
    source_file_name: str | None,
    source_file_type: str | None,
) -> MeetingRecord:
    err_list = errors_list_from_graph_result(result)
    err = encode_processing_errors(err_list)
    status = status_from_graph_result(result)
    return repo.create_record(
        participants=result.get("participants", ""),
        topics=result.get("topics", ""),
        actions=result.get("actions", ""),
        minutes=result.get("minutes", ""),
        executive_summary=result.get("executive_summary", ""),
        status=status,
        processing_errors=err,
        source_file_name=source_file_name,
        source_file_type=source_file_type,
    )


def persist_failed(
    repo: MeetingRepository,
    processing_errors: str | list[str],
    *,
    source_file_name: str | None = None,
    source_file_type: str | None = None,
) -> None:
    if isinstance(processing_errors, str):
        lst = [processing_errors.strip()] if processing_errors.strip() else []
    else:
        lst = [str(x).strip() for x in processing_errors if x and str(x).strip()]
    if not lst:
        lst = ["No se pudo completar el procesamiento."]
    encoded = encode_processing_errors(lst)
    repo.create_record(
        participants="",
        topics="",
        actions="",
        minutes="",
        executive_summary="",
        status="failed",
        processing_errors=encoded,
        source_file_name=source_file_name,
        source_file_type=source_file_type,
    )


def decode_stored_processing_errors(raw: str | None) -> list[str]:
    """Para capa API al leer filas ORM."""
    return decode_processing_errors(raw)
