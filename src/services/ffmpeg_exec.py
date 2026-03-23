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


def _ensure_ffmpeg_in_path(exe: str) -> str:
    """
    Si el binario no se llama "ffmpeg", crea un symlink en /tmp para que subprocess lo encuentre.

    imageio-ffmpeg proporciona binarios como ffmpeg-linux-aarch64-v7.0.2; Whisper invoca ``ffmpeg``.
    """
    exe_path = Path(exe).resolve()
    if exe_path.name == "ffmpeg":
        return str(exe_path.parent)

    link_dir = Path("/tmp/meetmind-ffmpeg-bin")
    link_path = link_dir / "ffmpeg"
    try:
        link_dir.mkdir(parents=True, exist_ok=True)
        if not link_path.exists() or link_path.resolve() != exe_path:
            if link_path.exists():
                link_path.unlink()
            link_path.symlink_to(exe_path)
    except OSError as e:
        logger.warning("No se pudo crear symlink ffmpeg: %s; fallback a directorio original", e)
        return str(exe_path.parent)
    return str(link_dir)


def prepend_ffmpeg_to_os_path() -> None:
    """
    Si solo existe el ffmpeg de imageio-ffmpeg, asegura que "ffmpeg" esté en PATH.

    Whisper invoca ``ffmpeg`` por nombre; imageio-ffmpeg usa nombres como ffmpeg-linux-aarch64-*.
    """
    if shutil.which("ffmpeg"):
        return
    exe = resolve_ffmpeg_executable()
    if not exe:
        return
    bin_dir = _ensure_ffmpeg_in_path(exe)
    path = os.environ.get("PATH", "")
    if bin_dir in path.split(os.pathsep):
        return
    os.environ["PATH"] = bin_dir + os.pathsep + path
    logger.info("PATH actualizado para incluir ffmpeg empaquetado: %s", bin_dir)
