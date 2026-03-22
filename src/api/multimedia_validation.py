"""Validación de archivos multimedia para el endpoint process/file."""

from pathlib import Path

from src.config import get_max_file_size_mb

# Extensiones permitidas (case-insensitive)
MULTIMEDIA_EXTENSIONS = {
    ".mp4", ".mov", ".mp3", ".wav", ".m4a", ".webm", ".mkv",
}
TEXT_EXTENSIONS = {".txt", ".md"}
ALL_ALLOWED_EXTENSIONS = MULTIMEDIA_EXTENSIONS | TEXT_EXTENSIONS

# MIME types aceptados (referencia)
MULTIMEDIA_MIME_TYPES = {
    "audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4",
    "video/mp4", "video/quicktime", "video/webm", "video/x-matroska",
}

MSG_FORMAT_UNSUPPORTED = (
    "Formato no soportado. Formatos permitidos: MP4, MOV, MP3, WAV, M4A, WEBM, MKV."
)
MSG_FILE_TOO_LARGE = "El archivo supera el límite de 500 MB."


def _get_max_bytes() -> int:
    return get_max_file_size_mb() * 1024 * 1024


def get_max_multimedia_bytes() -> int:
    """Límite de tamaño para archivos multimedia en bytes."""
    return _get_max_bytes()


def validate_multimedia_file(
    extension: str,
    content_type: str | None,
    size_bytes: int,
) -> str | None:
    """
    Valida archivo multimedia.

    Returns:
        Mensaje de error en español si no válido, None si válido.
    """
    ext = extension.lower() if extension else ""
    if not ext.startswith("."):
        ext = f".{ext}"

    if ext not in ALL_ALLOWED_EXTENSIONS:
        return MSG_FORMAT_UNSUPPORTED

    if ext in MULTIMEDIA_EXTENSIONS and size_bytes > _get_max_bytes():
        return MSG_FILE_TOO_LARGE.replace(
            "500", str(get_max_file_size_mb())
        )

    return None


def get_extension_from_filename(filename: str | None) -> str:
    """Extrae extensión del nombre de archivo."""
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def is_multimedia_extension(ext: str) -> bool:
    """Indica si la extensión es multimedia (audio o video)."""
    if not ext.startswith("."):
        ext = f".{ext}"
    return ext in MULTIMEDIA_EXTENSIONS
