"""Dependencias de FastAPI (inyección del grafo, etc.)."""

from collections.abc import Generator

from fastapi import Depends
from sqlmodel import Session

from src.agents.meeting.agent import get_graph
from src.db.database import get_engine
from src.db.repository import MeetingRepository


def get_graph_dep():
    """Retorna el grafo compilado para inyección en endpoints."""
    return get_graph()


def get_db_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session


def get_meeting_repository(session: Session = Depends(get_db_session)) -> MeetingRepository:
    return MeetingRepository(session)
