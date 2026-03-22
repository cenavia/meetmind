"""Router de comprobaciones de salud (liveness y readiness)."""

from fastapi import APIRouter, HTTPException

from src.db.database import check_database_connectivity

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness",
    description=(
        "Comprueba que el **proceso** del servicio responde. No valida base de datos ni "
        "dependencias externas; útil para reinicios y sondas ligeras."
    ),
)
def health() -> dict:
    """Liveness: el servicio HTTP está vivo."""
    return {"status": "ok"}


@router.get(
    "/ready",
    summary="Readiness",
    description=(
        "Comprueba que el servicio está **preparado** para operaciones que requieren el "
        "almacenamiento persistido (consulta mínima a la BD configurada)."
    ),
    responses={
        200: {"description": "Almacenamiento accesible"},
        503: {"description": "Servicio no preparado (p. ej. BD no accesible)"},
    },
)
def ready() -> dict:
    """Readiness: BD accesible para persistencia y lecturas de reuniones."""
    try:
        check_database_connectivity()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Servicio no preparado: el almacenamiento no está accesible.",
        ) from None
    return {"status": "ready"}
