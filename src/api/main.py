"""
MeetMind API - FastAPI application.

Ejecutar:
    uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

Health check:
    curl http://localhost:8000/health
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

from src.api.routers import health, process
from src.config import get_transcription_mode_label

logger = logging.getLogger("meetmind.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Transcripción multimedia: %s", get_transcription_mode_label())
    yield


app = FastAPI(
    title="MeetMind API",
    description="Sistema de procesamiento de reuniones con IA",
    version="0.1.0",
    lifespan=lifespan,
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
