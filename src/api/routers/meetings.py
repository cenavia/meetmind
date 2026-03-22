"""Lectura de reuniones persistidas."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, ConfigDict

from src.api.dependencies import get_meeting_repository
from src.db.repository import MeetingRepository

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
)


class MeetingRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    processing_errors: str | None


class MeetingRecordListResponse(BaseModel):
    items: list[MeetingRecordResponse]


@router.get(
    "",
    response_model=MeetingRecordListResponse,
    summary="Listar reuniones procesadas",
    description="Devuelve todas las reuniones almacenadas, más recientes primero. Lista vacía solo si la BD respondió y no hay filas.",
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
    return MeetingRecordListResponse(items=[MeetingRecordResponse.model_validate(r) for r in rows])


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
    return MeetingRecordResponse.model_validate(row)
