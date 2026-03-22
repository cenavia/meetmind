"""Tests unitarios para src.services.file_loader."""

import pytest

from src.services.file_loader import FileLoaderError, load_text_file


def test_load_text_file_utf8_success():
    """Archivo UTF-8 válido se carga correctamente."""
    content = "Reunión con Juan y María. Discutimos el presupuesto.".encode("utf-8")
    result = load_text_file(content, "notas.txt")
    assert result == "Reunión con Juan y María. Discutimos el presupuesto."


def test_load_text_file_md_extension():
    """Archivo .md se acepta."""
    content = "# Reunión\n\nTemas: presupuesto.".encode("utf-8")
    result = load_text_file(content, "notas.md")
    assert "Reunión" in result


def test_load_text_file_empty_raises():
    """Archivo vacío lanza FileLoaderError 422."""
    with pytest.raises(FileLoaderError) as exc_info:
        load_text_file(b"", "notas.txt")
    assert exc_info.value.status_code == 422
    assert "vacío" in exc_info.value.message


def test_load_text_file_whitespace_only_raises():
    """Archivo con solo espacios lanza FileLoaderError 422."""
    with pytest.raises(FileLoaderError) as exc_info:
        load_text_file(b"   \n\t  ", "notas.txt")
    assert exc_info.value.status_code == 422


def test_load_text_file_invalid_extension_raises():
    """Extensión no permitida lanza FileLoaderError 400."""
    with pytest.raises(FileLoaderError) as exc_info:
        load_text_file(b"content", "document.pdf")
    assert exc_info.value.status_code == 400
    assert ".txt" in exc_info.value.message and ".md" in exc_info.value.message


def test_load_text_file_length_limit_raises():
    """Contenido >50.000 caracteres lanza FileLoaderError 400."""
    content = ("x" * 50_001).encode("utf-8")
    with pytest.raises(FileLoaderError) as exc_info:
        load_text_file(content, "large.txt")
    assert exc_info.value.status_code == 400
    assert "50000" in exc_info.value.message


def test_load_text_file_utf8_special_chars():
    """Caracteres especiales UTF-8 (ñ, á, é) se decodifican correctamente."""
    content = "Reunión en Córdoba con José y María.".encode("utf-8")
    result = load_text_file(content, "notas.txt")
    assert result == "Reunión en Córdoba con José y María."


def test_load_text_file_latin1_fallback():
    """Archivo latin-1 se decodifica con fallback."""
    content = "Reuni\xf3n con Mar\xeda.".encode("latin-1")
    result = load_text_file(content, "notas.txt")
    assert "ó" in result or "Reunión" in result
    assert "í" in result or "María" in result


def test_load_text_file_latin1_fallback_for_invalid_utf8():
    """Bytes inválidos en UTF-8 se decodifican con fallback latin-1."""
    # Secuencia inválida en UTF-8 (continuation bytes sin start byte)
    content = b"\x80\x81\x82"
    # latin-1 acepta cualquier byte, así que decodifica correctamente
    result = load_text_file(content, "notas.txt")
    assert len(result) == 3
