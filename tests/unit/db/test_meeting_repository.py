"""Tests unitarios del repositorio de reuniones persistidas."""

import time
from uuid import uuid4

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from src.db.repository import MeetingRepository


@pytest.fixture
def repo_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_get_and_list_order(repo_session: Session) -> None:
    repo = MeetingRepository(repo_session)
    a = repo.create_record(
        participants="p1",
        topics="t1",
        actions="a1",
        minutes="m1",
        executive_summary="s1",
        status="completed",
    )
    time.sleep(0.02)
    b = repo.create_record(
        participants="p2",
        topics="t2",
        actions="a2",
        minutes="m2",
        executive_summary="s2",
        status="completed",
    )
    assert repo.get_by_id(a.id) is not None
    assert repo.get_by_id(b.id) is not None
    assert repo.get_by_id(uuid4()) is None

    ordered = repo.list_all_by_created_desc()
    assert len(ordered) == 2
    assert ordered[0].id == b.id
    assert ordered[1].id == a.id


def test_failed_record(repo_session: Session) -> None:
    repo = MeetingRepository(repo_session)
    row = repo.create_record(
        participants="",
        topics="",
        actions="",
        minutes="",
        executive_summary="",
        status="failed",
        processing_errors="Transcripción no disponible",
        source_file_name="x.mp3",
        source_file_type="audio/mpeg",
    )
    got = repo.get_by_id(row.id)
    assert got is not None
    assert got.status == "failed"
    assert got.processing_errors == "Transcripción no disponible"
    assert got.source_file_name == "x.mp3"
