"""Configuración del proyecto MeetMind."""

import os


def get_api_base_url() -> str:
    """URL base de la API (usado por la UI)."""
    return os.getenv("API_BASE_URL", "http://localhost:8000")
