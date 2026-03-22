"""
MeetMind API - FastAPI application.

Ejecutar:
    uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

Health (liveness): curl http://localhost:8000/health
Readiness:         curl http://localhost:8000/ready
"""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers import health, meetings, process
from src.db.database import init_db
from src.config import get_transcription_mode_label
from src.services.ffmpeg_exec import prepend_ffmpeg_to_os_path, resolve_ffmpeg_executable

logger = logging.getLogger("meetmind.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    prepend_ffmpeg_to_os_path()
    ff = resolve_ffmpeg_executable()
    if ff:
        logger.info("ffmpeg disponible: %s", ff)
    else:
        logger.warning("ffmpeg no encontrado: el video puede fallar hasta instalar dependencias o ffmpeg en el sistema")
    logger.info("Transcripción multimedia: %s", get_transcription_mode_label())
    init_db()
    yield


app = FastAPI(
    title="MeetMind API",
    description=(
        "API REST v1 para procesar reuniones (texto o archivo), consultar historial persistido "
        "y comprobar disponibilidad (`/health` liveness, `/ready` readiness). Documentación "
        "interactiva en `/docs`."
    ),
    version="0.2.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "health", "description": "Liveness y readiness del servicio"},
        {"name": "process", "description": "Procesamiento síncrono y streaming (SSE)"},
        {"name": "meetings", "description": "Lectura de reuniones almacenadas"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(process.router, prefix="/api/v1")
app.include_router(meetings.router, prefix="/api/v1")
