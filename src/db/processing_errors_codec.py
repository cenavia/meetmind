"""Serialización de `processing_errors` como JSON array en columna Text (spec 013)."""

from __future__ import annotations

import json
from typing import Any


def encode_processing_errors(messages: list[str]) -> str | None:
    """Codifica lista de mensajes a JSON array UTF-8. Vacío → None para BD."""
    cleaned = [m.strip() for m in messages if m and str(m).strip()]
    if not cleaned:
        return None
    return json.dumps(cleaned, ensure_ascii=False)


def decode_processing_errors(raw: str | None) -> list[str]:
    """
    Decodifica columna BD a lista. Tolerante a filas legacy (texto plano sin JSON).
    """
    if raw is None:
        return []
    s = raw.strip()
    if not s:
        return []
    try:
        data: Any = json.loads(s)
        if isinstance(data, list):
            return [str(x).strip() for x in data if str(x).strip()]
        if isinstance(data, str) and data.strip():
            return [data.strip()]
    except json.JSONDecodeError:
        pass
    return [s]
