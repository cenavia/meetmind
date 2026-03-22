"""Acceso a datos de reuniones persistidas."""

from uuid import UUID

from sqlmodel import Session, select

from src.db.models import MeetingRecord


class MeetingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_record(
        self,
        *,
        participants: str,
        topics: str,
        actions: str,
        minutes: str,
        executive_summary: str,
        status: str,
        processing_errors: str | None = None,
        source_file_name: str | None = None,
        source_file_type: str | None = None,
    ) -> MeetingRecord:
        row = MeetingRecord(
            participants=participants,
            topics=topics,
            actions=actions,
            minutes=minutes,
            executive_summary=executive_summary,
            status=status,
            processing_errors=processing_errors,
            source_file_name=source_file_name,
            source_file_type=source_file_type,
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return row

    def get_by_id(self, record_id: UUID) -> MeetingRecord | None:
        return self.session.get(MeetingRecord, record_id)

    def list_all_by_created_desc(self) -> list[MeetingRecord]:
        stmt = select(MeetingRecord).order_by(MeetingRecord.created_at.desc())
        return list(self.session.exec(stmt))
