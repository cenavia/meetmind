"""Utilidades para la UI Gradio de MeetMind."""

from pathlib import Path

ALLOWED_EXTENSIONS = frozenset(
    {".mp4", ".mov", ".mp3", ".wav", ".m4a", ".txt", ".md"}
)
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB

MSG_FORMATO_NO_SOPORTADO = (
    "Formato no soportado. Formatos permitidos: "
    "multimedia (MP4, MOV, MP3, WAV, M4A), texto (TXT, MD)."
)
MSG_ARCHIVO_DEMASIADO_GRANDE = "El archivo supera el límite de 500 MB."


def validate_file_extension(path: str | Path) -> str | None:
    """Valida que la extensión del archivo esté permitida.

    Returns:
        Mensaje de error en español si no es válido; None si es válido.
    """
    p = Path(path)
    ext = p.suffix.lower() if p.suffix else ""
    if ext not in {e.lower() for e in ALLOWED_EXTENSIONS}:
        return MSG_FORMATO_NO_SOPORTADO
    return None


def validate_file_size(path: str | Path) -> str | None:
    """Valida que el tamaño del archivo no exceda 500 MB.

    Returns:
        Mensaje de error en español si excede; None si es válido.
    """
    p = Path(path)
    if not p.exists():
        return "Archivo no encontrado."
    size = p.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        return MSG_ARCHIVO_DEMASIADO_GRANDE
    return None


def validate_file(path: str | Path) -> str | None:
    """Valida extensión y tamaño del archivo.

    Returns:
        Mensaje de error en español si no es válido; None si es válido.
    """
    err = validate_file_extension(path)
    if err:
        return err
    err = validate_file_size(path)
    if err:
        return err
    return None


# MIME types para multipart upload
EXTENSION_TO_MIME = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
}


def get_mime_for_extension(filename: str) -> str:
    """Devuelve el MIME type para la extensión del archivo.

    Si no se reconoce, usa application/octet-stream.
    """
    ext = Path(filename).suffix.lower()
    return EXTENSION_TO_MIME.get(ext, "application/octet-stream")
