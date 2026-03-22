"""
Transcripción de audio/video.

- **cloud**: API OpenAI `whisper-1` (requiere `OPENAI_API_KEY`). Límite ~25 MB por petición.
- **local**: paquete `openai-whisper` + PyTorch (`whisper.load_model` / `transcribe`).

En ambos modos, el video se prepara con **ffmpeg** (extracción de audio a WAV); el STT lo hace Whisper (API o local).
"""

from __future__ import annotations

import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

from src.config import (
    get_openai_transcription_max_bytes,
    get_transcription_backend,
    get_transcription_language,
    get_transcription_model,
    get_whisper_device,
)
from src.services.ffmpeg_exec import prepend_ffmpeg_to_os_path, resolve_ffmpeg_executable


class TranscriptionError(Exception):
    """Error al transcribir audio (codec no soportado, archivo corrupto, etc.)."""

    pass


_whisper_model = None
_whisper_loaded_key: str | None = None


def _resolve_torch_device() -> str:
    """Elige cuda / mps / cpu según hardware y WHISPER_DEVICE."""
    mode = get_whisper_device()
    try:
        import torch
    except ImportError:
        return "cpu"

    if mode == "cuda":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if mode == "mps":
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
    if mode == "cpu":
        return "cpu"
    # auto
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _get_model():
    """Carga y cachea el modelo Whisper local (modelo + dispositivo alineados con config)."""
    global _whisper_model, _whisper_loaded_key
    import whisper

    model_name = get_transcription_model()
    device = _resolve_torch_device()
    cache_key = f"{model_name}:{device}"

    if _whisper_model is None or _whisper_loaded_key != cache_key:
        _whisper_model = whisper.load_model(model_name, device=device)
        _whisper_loaded_key = cache_key
    return _whisper_model


def _is_video_ext(path: str | Path) -> bool:
    """Indica si la extensión corresponde a video."""
    ext = Path(path).suffix.lower()
    return ext in {".mp4", ".mov", ".webm", ".mkv"}


def _extract_audio_from_video(video_path: Path) -> Path:
    """Extrae pista de audio de video a WAV temporal. Usa ffmpeg del sistema o imageio-ffmpeg."""
    prepend_ffmpeg_to_os_path()
    ffmpeg_bin = resolve_ffmpeg_executable()
    if not ffmpeg_bin:
        msg = (
            "Para procesar archivos de video (MP4, MOV, WEBM, MKV) hace falta ffmpeg. "
            "Instala dependencias del proyecto (incluye imageio-ffmpeg) o instala ffmpeg en el sistema."
        )
        logger.warning("ffmpeg no encontrado: no se puede procesar video")
        raise TranscriptionError(msg)
    fd, wav_path = tempfile.mkstemp(suffix=".wav")
    try:
        os.close(fd)
        result = subprocess.run(
            [
                ffmpeg_bin,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                "-ac",
                "1",
                str(wav_path),
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            logger.warning(
                "ffmpeg falló: returncode=%s stderr=%s",
                result.returncode,
                result.stderr[:500] if result.stderr else "",
            )
            raise TranscriptionError(
                "El formato del archivo no es compatible. Verifica que el video tenga una pista de audio válida."
            )
        return Path(wav_path)
    except subprocess.TimeoutExpired:
        if Path(wav_path).exists():
            Path(wav_path).unlink(missing_ok=True)
        raise TranscriptionError("No se pudo procesar el archivo. Verifica que no esté dañado.")
    except Exception as e:
        if Path(wav_path).exists():
            Path(wav_path).unlink(missing_ok=True)
        if isinstance(e, TranscriptionError):
            raise
        raise TranscriptionError("El formato del archivo no es compatible.") from e


def _transcribe_openai_cloud(path: Path, *, language: str | None) -> str:
    """Transcribe con la API de OpenAI (modelo whisper-1)."""
    api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    if not api_key:
        raise TranscriptionError(
            "Falta OPENAI_API_KEY para transcripción en la nube. "
            "Configura la variable o usa TRANSCRIPTION_BACKEND=local."
        )

    max_bytes = get_openai_transcription_max_bytes()
    size = path.stat().st_size
    if size > max_bytes:
        raise TranscriptionError(
            "El audio a transcribir supera el límite de la API de OpenAI (25 MB por archivo). "
            "Usa un archivo más corto o menor calidad, o TRANSCRIPTION_BACKEND=local."
        )

    try:
        from openai import APIConnectionError, APIStatusError, AuthenticationError, OpenAI, RateLimitError
    except ImportError as e:
        raise TranscriptionError(
            "No está instalado el paquete 'openai'. Ejecuta: uv sync"
        ) from e

    client = OpenAI(api_key=api_key)

    kwargs: dict = {"model": "whisper-1"}
    if language:
        kwargs["language"] = language

    try:
        with open(path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                file=(path.name, audio_file),
                **kwargs,
            )
    except AuthenticationError as e:
        logger.warning("OpenAI transcription: autenticación fallida")
        raise TranscriptionError(
            "La clave de OpenAI no es válida o ha expirado. Revisa OPENAI_API_KEY."
        ) from e
    except RateLimitError as e:
        logger.warning("OpenAI transcription: rate limit")
        raise TranscriptionError(
            "Límite de uso de la API de OpenAI alcanzado. Intenta más tarde."
        ) from e
    except APIConnectionError as e:
        logger.warning("OpenAI transcription: error de conexión: %s", e)
        raise TranscriptionError(
            "No se pudo conectar con el servicio de transcripción. Comprueba tu red."
        ) from e
    except APIStatusError as e:
        logger.warning("OpenAI transcription: HTTP %s %s", e.status_code, e.message)
        if e.status_code == 413:
            raise TranscriptionError(
                "El archivo es demasiado grande para la API de transcripción."
            ) from e
        raise TranscriptionError(
            "El servicio de transcripción rechazó el archivo. Verifica formato y tamaño."
        ) from e

    text = (getattr(transcript, "text", None) or "").strip()
    return text


def _transcribe_local_whisper(path: Path, *, language: str | None) -> str:
    """Transcribe con openai-whisper local."""
    whisper_model = _get_model()
    lang = language
    device = _resolve_torch_device()
    use_fp16 = device == "cuda"

    result = whisper_model.transcribe(
        str(path),
        language=lang,
        fp16=use_fp16,
    )
    return (result.get("text") or "").strip()


def transcribe_audio(
    audio_path: str | Path,
    *,
    model: str | None = None,
    language: str | None = None,
) -> str:
    """
    Transcribe un archivo de audio a texto.

    Args:
        audio_path: Ruta al archivo de audio (MP3, WAV, M4A) o video (se extrae audio).
        model: Solo aplica a modo **local**; ignorado en cloud (siempre whisper-1 en API).
        language: Código de idioma (ej. "es", "en") o None para autodetección.

    Returns:
        Texto transcrito.

    Raises:
        TranscriptionError: Si el archivo no puede procesarse (codec no soportado, corrupto).
    """
    _ = model  # reservado para futura API; cloud usa whisper-1 fijo

    path = Path(audio_path)
    if not path.exists():
        raise TranscriptionError("No se pudo procesar el archivo. Verifica que no esté dañado.")

    # Whisper puede llamar a `ffmpeg` por nombre para algunos formatos
    prepend_ffmpeg_to_os_path()

    temp_wav: Path | None = None
    try:
        if _is_video_ext(path):
            temp_wav = _extract_audio_from_video(path)
            path = temp_wav

        lang = language if language is not None else get_transcription_language()
        backend = get_transcription_backend()

        if backend == "cloud":
            text = _transcribe_openai_cloud(path, language=lang)
        else:
            text = _transcribe_local_whisper(path, language=lang)

        return text
    except TranscriptionError:
        raise
    except Exception as e:
        if isinstance(e, TranscriptionError):
            raise
        logger.exception("Error al transcribir %s: %s", audio_path, e)
        msg = "El formato del archivo no es compatible."
        if "ffmpeg" in str(e).lower() or "no such file" in str(e).lower():
            msg = "No se pudo procesar el archivo. Verifica que no esté dañado."
        raise TranscriptionError(msg) from e
    finally:
        if temp_wav and temp_wav.exists():
            temp_wav.unlink(missing_ok=True)
