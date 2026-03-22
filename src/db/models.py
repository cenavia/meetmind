"""Modelos de tablas SQLModel."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MeetingRecord(SQLModel, table=True):
    """Una ejecución persistida del procesamiento de reunión."""

    __tablename__ = "meeting_record"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    participants: str = Field(default="", sa_column=Column(Text, nullable=False))
    topics: str = Field(default="", sa_column=Column(Text, nullable=False))
    actions: str = Field(default="", sa_column=Column(Text, nullable=False))
    minutes: str = Field(default="", sa_column=Column(Text, nullable=False))
    executive_summary: str = Field(default="", sa_column=Column(Text, nullable=False))
    source_file_name: Optional[str] = Field(default=None, max_length=1024)
    source_file_type: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(max_length=32)
    created_at: datetime = Field(default_factory=_utc_now)
    processing_errors: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
