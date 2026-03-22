"""Lectura de reuniones persistidas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from src.api.dependencies import get_meeting_repository
from src.db.meeting_persist import decode_stored_processing_errors
from src.db.models import MeetingRecord
from src.db.repository import MeetingRepository

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)


class MeetingRecordResponse(BaseModel):
    """DTO de lectura; `processing_errors` como lista (spec 013). Ver contrato processing-feedback.md."""

    id: UUID
    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str
    source_file_name: str | None
    source_file_type: str | None
    status: str
    created_at: datetime
    processing_errors: list[str]

    @classmethod
    def from_row(cls, row: MeetingRecord) -> MeetingRecordResponse:
        return cls(
            id=row.id,
            participants=row.participants,
            topics=row.topics,
            actions=row.actions,
            minutes=row.minutes,
            executive_summary=row.executive_summary,
            source_file_name=row.source_file_name,
            source_file_type=row.source_file_type,
            status=row.status,
            created_at=row.created_at,
            processing_errors=decode_stored_processing_errors(row.processing_errors),
        )


class MeetingRecordListResponse(BaseModel):
    items: list[MeetingRecordResponse]


@router.get(
    "",
    response_model=MeetingRecordListResponse,
    summary="Listar reuniones procesadas",
    description=(
        "Devuelve todas las reuniones almacenadas, más recientes primero. Lista vacía solo si la BD respondió y no hay filas. "
        "Cada ítem incluye `processing_errors` como **lista** de strings (spec 013, contrato "
        "`specs/013-incomplete-error-feedback/contracts/processing-feedback.md`)."
    ),
    responses={
        200: {"description": "Lista obtenida (puede estar vacía)"},
        503: {"description": "No se pudo acceder al almacenamiento"},
    },
)
def list_meetings(repo: MeetingRepository = Depends(get_meeting_repository)) -> MeetingRecordListResponse:
    try:
        rows = repo.list_all_by_created_desc()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo acceder al almacenamiento de reuniones. Intenta de nuevo más tarde.",
        ) from None
    return MeetingRecordListResponse(items=[MeetingRecordResponse.from_row(r) for r in rows])


@router.get(
    "/{meeting_id}",
    response_model=MeetingRecordResponse,
    summary="Detalle de reunión por id",
    description="Recupera un registro persistido por UUID.",
    responses={
        200: {"description": "Registro encontrado"},
        404: {"description": "No existe reunión con ese id"},
        503: {"description": "No se pudo acceder al almacenamiento"},
    },
)
def get_meeting(
    meeting_id: UUID,
    repo: MeetingRepository = Depends(get_meeting_repository),
) -> MeetingRecordResponse:
    try:
        row = repo.get_by_id(meeting_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="No se pudo acceder al almacenamiento de reuniones. Intenta de nuevo más tarde.",
        ) from None
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="No existe ninguna reunión con ese identificador.",
        )
    return MeetingRecordResponse.from_row(row)
