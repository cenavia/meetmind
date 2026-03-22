"""Tests de validación de archivos para la UI."""

import tempfile
from pathlib import Path

import pytest

from src.ui.utils import (
    MSG_ARCHIVO_DEMASIADO_GRANDE,
    MSG_FORMATO_NO_SOPORTADO,
    get_mime_for_extension,
    validate_file,
    validate_file_extension,
    validate_file_size,
)


class TestValidateFileExtension:
    def test_valid_extensions(self):
        """Extensiones permitidas devuelven None."""
        for ext in [".txt", ".md", ".mp4", ".mov", ".mp3", ".wav", ".m4a"]:
            assert validate_file_extension(f"archivo{ext}") is None
            assert validate_file_extension(f"archivo{ext.upper()}") is None

    def test_invalid_extension_exe(self):
        """Extensión .exe devuelve mensaje de error."""
        result = validate_file_extension("malware.exe")
        assert result == MSG_FORMATO_NO_SOPORTADO

    def test_invalid_extension_zip(self):
        """Extensión .zip devuelve mensaje de error."""
        result = validate_file_extension("archivo.zip")
        assert result == MSG_FORMATO_NO_SOPORTADO

    def test_empty_extension(self):
        """Sin extensión devuelve mensaje de error."""
        result = validate_file_extension("archivosinext")
        assert result == MSG_FORMATO_NO_SOPORTADO


class TestValidateFileSize:
    def test_file_within_limit(self, tmp_path):
        """Archivo pequeño devuelve None."""
        f = tmp_path / "test.txt"
        f.write_text("hola")
        assert validate_file_size(f) is None

    def test_file_exceeds_limit(self, tmp_path):
        """Archivo >500 MB devuelve mensaje de error."""
        f = tmp_path / "huge.bin"
        # Crear archivo > 500 MB (solo reservamos espacio en sistemas que lo permitan)
        try:
            with open(f, "wb") as fp:
                fp.seek(500 * 1024 * 1024 + 1)
                fp.write(b"x")
        except OSError:
            pytest.skip("Sistema no permite crear archivos tan grandes")
        assert validate_file_size(f) == MSG_ARCHIVO_DEMASIADO_GRANDE

    def test_nonexistent_file(self):
        """Archivo inexistente devuelve mensaje de error."""
        result = validate_file_size("/ruta/que/no/existe.txt")
        assert result == "Archivo no encontrado."


class TestValidateFile:
    def test_valid_file(self, tmp_path):
        """Archivo válido (extensión y tamaño) devuelve None."""
        f = tmp_path / "notas.txt"
        f.write_text("Reunión con Juan.")
        assert validate_file(f) is None

    def test_invalid_extension_returns_message(self, tmp_path):
        """Extensión inválida devuelve mensaje correcto."""
        f = tmp_path / "virus.exe"
        f.write_text("malware")
        assert validate_file(f) == MSG_FORMATO_NO_SOPORTADO

    def test_oversize_returns_message(self, tmp_path):
        """Archivo >500 MB devuelve mensaje correcto."""
        f = tmp_path / "huge.mp4"
        try:
            with open(f, "wb") as fp:
                fp.seek(500 * 1024 * 1024 + 1)
                fp.write(b"x")
        except OSError:
            pytest.skip("Sistema no permite crear archivos tan grandes")
        assert validate_file(f) == MSG_ARCHIVO_DEMASIADO_GRANDE

    def test_extension_checked_before_size(self, tmp_path):
        """La extensión se valida antes que el tamaño."""
        f = tmp_path / "malware.exe"
        f.write_text("x")
        assert validate_file(f) == MSG_FORMATO_NO_SOPORTADO


class TestGetMimeForExtension:
    def test_known_extensions(self):
        """Extensiones conocidas devuelven MIME correcto."""
        assert get_mime_for_extension("a.txt") == "text/plain"
        assert get_mime_for_extension("a.md") == "text/markdown"
        assert get_mime_for_extension("a.mp4") == "video/mp4"
        assert get_mime_for_extension("a.mp3") == "audio/mpeg"
        assert get_mime_for_extension("a.wav") == "audio/wav"
        assert get_mime_for_extension("a.m4a") == "audio/mp4"

    def test_unknown_extension(self):
        """Extensión desconocida devuelve application/octet-stream."""
        assert get_mime_for_extension("a.xyz") == "application/octet-stream"
