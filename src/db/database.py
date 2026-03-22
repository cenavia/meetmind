"""Motor SQL y creación de tablas."""

from sqlmodel import SQLModel, create_engine

from src.config import get_database_url

_engine = None


def get_engine():
    """Motor singleton (lazy) para respetar DATABASE_URL tras monkeypatch en tests."""
    global _engine
    if _engine is None:
        url = get_database_url()
        connect_args: dict = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(url, connect_args=connect_args)
    return _engine


def reset_db_engine() -> None:
    """Libera el motor (p. ej. entre tests con otra DATABASE_URL)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


def init_db() -> None:
    """Crea tablas si no existen (MVP sin Alembic)."""
    # Importar modelos para registrar metadata
    from src.db import models  # noqa: F401

    SQLModel.metadata.create_all(get_engine())
