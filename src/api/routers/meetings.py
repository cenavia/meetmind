"""Lectura de reuniones persistidas."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from src.api.dependencies import get_meeting_repository
from src.db.repository import MeetingRepository

router = APIRouter(prefix="/meetings", tags=["meetings"])


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


@router.get("", response_model=MeetingRecordListResponse)
def list_meetings(repo: MeetingRepository = Depends(get_meeting_repository)) -> MeetingRecordListResponse:
    rows = repo.list_all_by_created_desc()
    return MeetingRecordListResponse(items=[MeetingRecordResponse.model_validate(r) for r in rows])


@router.get("/{meeting_id}", response_model=MeetingRecordResponse)
def get_meeting(
    meeting_id: UUID,
    repo: MeetingRepository = Depends(get_meeting_repository),
) -> MeetingRecordResponse:
    row = repo.get_by_id(meeting_id)
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="No existe ninguna reunión con ese identificador.",
        )
    return MeetingRecordResponse.model_validate(row)
