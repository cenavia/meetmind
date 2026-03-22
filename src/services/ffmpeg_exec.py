"""
Resolución del ejecutable **ffmpeg** (video → audio, y decodificación que use Whisper).

1. Si hay `ffmpeg` en el **PATH** del sistema, se usa (prioridad).
2. Si no, se usa el binario que trae el paquete **imageio-ffmpeg** (instalable con el proyecto vía `uv`/`pip`).

No sustituye a “la nube”: es procesamiento **local** del contenedor de vídeo/audio.
"""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

_ffmpeg_cached: str | None | bool = False  # False = no calculado aún


def resolve_ffmpeg_executable() -> str | None:
    """
    Devuelve la ruta absoluta al binario ffmpeg, o None si no hay ninguno disponible.
    """
    global _ffmpeg_cached
    if _ffmpeg_cached is not False:
        return _ffmpeg_cached  # type: ignore[return-value]

    system = shutil.which("ffmpeg")
    if system:
        _ffmpeg_cached = system
        logger.debug("ffmpeg del sistema: %s", system)
        return system

    try:
        import imageio_ffmpeg

        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and Path(bundled).exists():
            _ffmpeg_cached = str(Path(bundled).resolve())
            logger.info("Usando ffmpeg empaquetado (imageio-ffmpeg): %s", _ffmpeg_cached)
            return _ffmpeg_cached
    except Exception as e:
        logger.debug("imageio-ffmpeg no proporciona ffmpeg: %s", e)

    _ffmpeg_cached = None
    return None


def prepend_ffmpeg_to_os_path() -> None:
    """
    Si solo existe el ffmpeg de imageio-ffmpeg, añade su carpeta al PATH del proceso.

    Whisper/openai-whisper a veces invoca `ffmpeg` por nombre; así lo encuentran sin brew/apt.
    """
    if shutil.which("ffmpeg"):
        return
    exe = resolve_ffmpeg_executable()
    if not exe:
        return
    bin_dir = str(Path(exe).resolve().parent)
    path = os.environ.get("PATH", "")
    if bin_dir in path.split(os.pathsep):
        return
    os.environ["PATH"] = bin_dir + os.pathsep + path
    logger.info("PATH actualizado para incluir ffmpeg empaquetado: %s", bin_dir)
