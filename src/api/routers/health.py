"""Router de health check."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Health check del servicio."""
    return {"status": "ok"}
