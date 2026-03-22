"""Tests unitarios para el servicio de transcripción."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.transcription import (
    TranscriptionError,
    transcribe_audio,
)


@patch("src.services.transcription._get_model")
def test_transcribe_audio_returns_text(mock_get_model):
    """transcribe_audio retorna el texto transcrito."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "  Hola, esta es una reunión.  "}
    mock_get_model.return_value = mock_model

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake mp3")
        tmp_path = f.name

    try:
        with patch("src.services.transcription._is_video_ext", return_value=False):
            result = transcribe_audio(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    assert result == "Hola, esta es una reunión."
    mock_model.transcribe.assert_called_once()


@patch("src.services.transcription._get_model")
def test_transcribe_audio_raises_on_transcription_failure(mock_get_model):
    """transcribe_audio lanza TranscriptionError cuando Whisper falla."""
    mock_model = MagicMock()
    mock_model.transcribe.side_effect = RuntimeError("Codec not supported")
    mock_get_model.return_value = mock_model

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake")
        tmp_path = f.name

    try:
        with patch("src.services.transcription._is_video_ext", return_value=False):
            with pytest.raises(TranscriptionError) as exc_info:
                transcribe_audio(tmp_path)
        msg = exc_info.value.args[0].lower()
        assert "formato" in msg or "procesar" in msg
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@patch("src.services.transcription._get_model")
def test_transcribe_audio_empty_result_returns_empty_string(mock_get_model):
    """transcribe_audio retorna '' cuando la transcripción está vacía."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": ""}
    mock_get_model.return_value = mock_model

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake")
        tmp_path = f.name

    try:
        with patch("src.services.transcription._is_video_ext", return_value=False):
            result = transcribe_audio(tmp_path)
        assert result == ""
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@patch("src.services.transcription._get_model")
def test_transcribe_audio_valid_mp3_path_through_transcription(mock_get_model):
    """transcribe_audio procesa correctamente un path a MP3 (mock)."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "Texto de prueba transcrito"}
    mock_get_model.return_value = mock_model

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake mp3 content")
        tmp_path = f.name

    try:
        with patch("src.services.transcription._is_video_ext", return_value=False):
            result = transcribe_audio(tmp_path)
        assert result == "Texto de prueba transcrito"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_transcribe_audio_file_not_found_raises():
    """transcribe_audio lanza TranscriptionError si el archivo no existe."""
    with pytest.raises(TranscriptionError) as exc_info:
        transcribe_audio("/nonexistent/path.mp3")

    msg = exc_info.value.args[0].lower()
    assert "procesar" in msg or "dañado" in msg


@patch("src.services.transcription._transcribe_openai_cloud")
@patch("src.services.transcription.get_transcription_backend")
def test_transcribe_audio_uses_cloud_when_configured(mock_backend, mock_cloud):
    """Con backend cloud se delega a la API de OpenAI (sin cargar Whisper local)."""
    mock_backend.return_value = "cloud"
    mock_cloud.return_value = "Texto desde la nube"

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(b"fake")
        tmp_path = f.name

    try:
        with patch("src.services.transcription._is_video_ext", return_value=False):
            result = transcribe_audio(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    assert result == "Texto desde la nube"
    mock_cloud.assert_called_once()
    assert mock_cloud.call_args[0][0] == Path(tmp_path)
