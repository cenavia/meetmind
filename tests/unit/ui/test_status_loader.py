"""Tests del panel de estado (loader)."""

from src.ui.status_loader import (
    loader_custom,
    loader_idle,
    loader_multimedia,
    multimedia_phase_from_elapsed,
)


def test_loader_idle_empty():
    assert loader_idle() == ""


def test_loader_multimedia_contains_phase_title():
    html = loader_multimedia(2, elapsed_sec=10.0, hint="hint")
    assert "Transcripción" in html
    assert "10" in html
    assert "hint" in html


def test_loader_custom_shows_cloud_badge():
    html = loader_custom(
        title="T",
        description="D",
        transcription_backend="cloud",
    )
    assert "NUBE" in html
    assert "OpenAI" in html


def test_loader_custom_shows_none_badge_for_text_only():
    html = loader_custom(title="T", description="D", transcription_backend="none")
    assert "SIN WHISPER" in html


def test_multimedia_phase_from_elapsed():
    assert multimedia_phase_from_elapsed(0) == 1
    assert multimedia_phase_from_elapsed(3.9) == 1
    assert multimedia_phase_from_elapsed(4) == 2
    assert multimedia_phase_from_elapsed(119) == 2
    assert multimedia_phase_from_elapsed(120) == 3
