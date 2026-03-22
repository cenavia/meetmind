"""Configuración del proyecto MeetMind."""

import logging
import os
from pathlib import Path
from typing import Literal

from sqlalchemy.engine.url import make_url

logger = logging.getLogger(__name__)


def get_api_base_url() -> str:
    """URL base de la API (usado por la UI)."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")


def _sqlite_url_with_writable_parent(url: str) -> str:
    """
    Crea el directorio padre del fichero SQLite si falta.

    Si la ruta no es usable (p. ej. ``DATABASE_URL`` apunta a un path del host
    dentro de Docker), usa ``/tmp/meetmind.db`` para evitar
    ``unable to open database file``.
    """
    if not url.startswith("sqlite"):
        return url
    try:
        parsed = make_url(url)
    except Exception:
        return url
    db = parsed.database
    if not db or db == ":memory:":
        return url
    path = Path(db)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        return url
    except OSError as e:
        logger.warning(
            "SQLite: no se puede usar el directorio %s (%s); fallback a /tmp/meetmind.db",
            parent,
            e,
        )
        return "sqlite:////tmp/meetmind.db"


def get_database_url() -> str:
    """URL SQLAlchemy para persistencia (SQLite por defecto en el directorio de trabajo)."""
    raw = os.getenv("DATABASE_URL", "").strip()
    if raw:
        return _sqlite_url_with_writable_parent(raw)
    return _sqlite_url_with_writable_parent("sqlite:///./meetmind.db")


# Modelos Whisper válidos (multilingües; sin sufijo .en para español/reuniones mixtas)
WHISPER_MODELS = frozenset(
    {"tiny", "base", "small", "medium", "large", "large-v2", "large-v3"}
)


def get_transcription_backend() -> Literal["local", "cloud"]:
    """
    Motor de transcripción: **cloud** (API OpenAI `whisper-1`) o **local** (`openai-whisper`).

    Requiere `OPENAI_API_KEY` si `cloud`. Por defecto **cloud** si hay clave, si no **local**.
    Override explícito: TRANSCRIPTION_BACKEND=cloud | local.
    """
    explicit = (os.getenv("TRANSCRIPTION_BACKEND") or "").strip().lower()
    if explicit in ("local", "cloud"):
        return explicit  # type: ignore[return-value]
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    return "cloud" if key else "local"


def get_transcription_mode_label() -> str:
    """
    Texto fijo para mostrar en UI o logs: dónde se ejecuta Whisper.

    - **cloud**: API OpenAI `whisper-1`
    - **local**: paquete `openai-whisper` en la máquina que corre la API
    """
    if get_transcription_backend() == "cloud":
        return "NUBE — Whisper vía OpenAI API (whisper-1)"
    return "LOCAL — Whisper en este servidor (openai-whisper + PyTorch)"


def get_openai_transcription_max_bytes() -> int:
    """Límite de tamaño del archivo enviado a la API de transcripción (por defecto 25 MB)."""
    val = os.getenv("OPENAI_TRANSCRIPTION_MAX_MB", "25")
    try:
        mb = int(val)
        return max(1, mb) * 1024 * 1024
    except ValueError:
        return 25 * 1024 * 1024


def get_transcription_model() -> str:
    """
    Modelo Whisper para transcripción.

    Por defecto **small**: mejor relación calidad/tiempo que `base` para voz
    conversacional y español; más ligero que `medium`/`large`.

    Override: TRANSCRIPTION_MODEL (tiny, base, small, medium, large, large-v2, large-v3).
    """
    raw = (os.getenv("TRANSCRIPTION_MODEL") or "small").strip().lower()
    return raw if raw in WHISPER_MODELS else "small"


def get_transcription_language() -> str | None:
    """
    Idioma forzado para Whisper (ISO 639-1), o None = autodetección.

    Por defecto **es** (reuniones MeetMind en español): menos errores que autodetect.
    Para multilingüe real: TRANSCRIPTION_LANGUAGE= (vacío) o no definir y usar env vacío.

    Valores: TRANSCRIPTION_LANGUAGE=es | en | fr | ... | vacío para autodetectar.
    """
    val = os.getenv("TRANSCRIPTION_LANGUAGE")
    if val is None:
        return "es"
    stripped = val.strip()
    return stripped if stripped else None


def get_whisper_device() -> str:
    """
    Dispositivo para Whisper: auto | cuda | cpu | mps.

    Por defecto **auto**: CUDA si hay GPU NVIDIA, MPS en Apple Silicon, si no CPU.
    """
    raw = (os.getenv("WHISPER_DEVICE") or "auto").strip().lower()
    if raw in ("cuda", "cpu", "mps"):
        return raw
    return "auto"


def get_max_file_size_mb() -> int:
    """Límite de tamaño de archivo multimedia en MB (por defecto 500)."""
    val = os.getenv("MAX_FILE_SIZE_MB", "500")
    try:
        return int(val)
    except ValueError:
        return 500


def get_processing_timeout_sec() -> int:
    """Timeout de procesamiento en segundos (por defecto 900 = 15 min)."""
    val = os.getenv("PROCESSING_TIMEOUT_SEC", "900")
    try:
        return int(val)
    except ValueError:
        return 900


def get_meeting_min_words() -> int:
    """
    Umbral mínimo de palabras para considerar el texto de reunión “muy corto” (advertencia).

    Por defecto **20**; override con `MEETING_MIN_WORDS` (entero ≥ 1).
    """
    val = os.getenv("MEETING_MIN_WORDS", "20")
    try:
        n = int(val)
        return max(1, n)
    except ValueError:
        return 20
