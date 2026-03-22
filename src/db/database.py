"""Motor SQL y creación de tablas.

La función :func:`check_database_connectivity` sirve para **readiness** (sondas de
“servicio preparado”): comprueba que el almacenamiento configurado responde.

**Liveness** (solo “¿el proceso responde?”) no debe depender de la BD; usar
``GET /health`` sin llamar a esta función.
"""

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

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


def check_database_connectivity() -> None:
    """Ejecuta una consulta mínima contra la BD configurada.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: si no hay conexión o la consulta falla.
    """
    with Session(get_engine()) as session:
        session.execute(text("SELECT 1"))
