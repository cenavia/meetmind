"""Tests para resolución de ffmpeg."""

import pytest
from unittest.mock import patch

from src.services import ffmpeg_exec


@pytest.fixture(autouse=True)
def _reset_ffmpeg_cache():
    ffmpeg_exec._ffmpeg_cached = False  # type: ignore[misc]
    yield
    ffmpeg_exec._ffmpeg_cached = False  # type: ignore[misc]


def test_resolve_ffmpeg_prefers_system(monkeypatch, tmp_path):
    """Si hay ffmpeg en PATH, se usa."""
    fake = tmp_path / "ffmpeg"
    fake.write_text("#!/bin/sh\necho ok")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    ffmpeg_exec._ffmpeg_cached = False  # type: ignore[misc]
    assert ffmpeg_exec.resolve_ffmpeg_executable() == str(fake)


@patch("src.services.ffmpeg_exec.shutil.which", return_value=None)
@patch("imageio_ffmpeg.get_ffmpeg_exe", return_value="/bundled/ffmpeg")
def test_resolve_ffmpeg_fallback_imageio(mock_exe, mock_which, tmp_path):
    """Sin ffmpeg en PATH, usa imageio-ffmpeg."""
    bundled = tmp_path / "ffmpeg"
    bundled.write_text("x")
    bundled.chmod(0o755)
    mock_exe.return_value = str(bundled)
    ffmpeg_exec._ffmpeg_cached = False  # type: ignore[misc]
    assert ffmpeg_exec.resolve_ffmpeg_executable() == str(bundled.resolve())
