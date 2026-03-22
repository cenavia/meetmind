"""Configuración global de pytest."""

import pytest


@pytest.fixture(autouse=True)
def _transcription_backend_local_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita llamadas reales a OpenAI si OPENAI_API_KEY está definido en el entorno."""
    monkeypatch.setenv("TRANSCRIPTION_BACKEND", "local")
