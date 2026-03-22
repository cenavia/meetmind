"""Reglas de persistencia tras procesamiento (capa API)."""

from src.db.models import MeetingRecord
from src.db.repository import MeetingRepository

LIMITED_PREFIX = "[Información limitada]"


def status_from_graph_result(result: dict) -> str:
    """Deriva completed vs partial según spec/tasks (T010)."""
    pe = (result.get("processing_errors") or "").strip()
    if pe:
        return "partial"
    minutes = (result.get("minutes") or "").strip()
    summary = (result.get("executive_summary") or "").strip()
    if minutes.startswith(LIMITED_PREFIX) or summary.startswith(LIMITED_PREFIX):
        return "partial"
    return "completed"


def persist_graph_success(
    repo: MeetingRepository,
    result: dict,
    *,
    source_file_name: str | None,
    source_file_type: str | None,
) -> MeetingRecord:
    status = status_from_graph_result(result)
    err = (result.get("processing_errors") or "").strip() or None
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
    processing_errors: str,
    *,
    source_file_name: str | None = None,
    source_file_type: str | None = None,
) -> None:
    repo.create_record(
        participants="",
        topics="",
        actions="",
        minutes="",
        executive_summary="",
        status="failed",
        processing_errors=processing_errors,
        source_file_name=source_file_name,
        source_file_type=source_file_type,
    )
