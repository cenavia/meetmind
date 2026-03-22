"""Servicio de carga de archivos de texto (TXT, Markdown)."""

from pathlib import Path

ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_CONTENT_LENGTH = 50_000
ENCODING_FALLBACK = ("utf-8", "latin-1")


class FileLoaderError(Exception):
    """Error al cargar un archivo de texto."""

    def __init__(self, message: str, status_code: int = 422):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _validate_extension(filename: str) -> str:
    """Valida la extensión del archivo. Retorna la extensión o lanza FileLoaderError."""
    path = Path(filename)
    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise FileLoaderError(
            "Solo se admiten archivos .txt y .md",
            status_code=400,
        )
    return ext


def load_text_file(content: bytes, filename: str) -> str:
    """
    Carga el contenido de un archivo de texto (.txt o .md).

    Args:
        content: Contenido en bytes del archivo.
        filename: Nombre del archivo (para validar extensión).

    Returns:
        Contenido como string decodificado.

    Raises:
        FileLoaderError: Si la extensión no es válida, el archivo está vacío,
            excede el límite de caracteres, o no se puede decodificar.
    """
    _validate_extension(filename)

    if not content or not content.strip():
        raise FileLoaderError(
            "El archivo está vacío o contiene solo espacios",
            status_code=422,
        )

    text: str | None = None
    last_error: Exception | None = None

    for encoding in ENCODING_FALLBACK:
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError as e:
            last_error = e
            continue

    if text is None:
        raise FileLoaderError(
            "No se pudo interpretar el encoding del archivo. Use UTF-8 o Latin-1.",
            status_code=422,
        )

    text = text.strip()
    if not text:
        raise FileLoaderError(
            "El archivo está vacío o contiene solo espacios",
            status_code=422,
        )

    if len(text) > MAX_CONTENT_LENGTH:
        raise FileLoaderError(
            f"El contenido excede el límite de {MAX_CONTENT_LENGTH} caracteres",
            status_code=400,
        )

    return text
