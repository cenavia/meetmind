"""Cliente ligero para respuestas SSE de la API MeetMind."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx


def iter_sse_events(response: httpx.Response) -> Iterator[dict[str, Any]]:
    """
    Parsea eventos `data: {...}` de una respuesta HTTP en streaming.

    Acumula texto hasta bloques separados por línea en blanco (convención SSE).
    """
    buf = ""
    for chunk in response.iter_text():
        buf += chunk
        while "\n\n" in buf:
            block, buf = buf.split("\n\n", 1)
            for line in block.split("\n"):
                line = line.strip()
                if line.startswith("data:"):
                    raw = line[5:].strip()
                    if raw:
                        yield json.loads(raw)


def read_http_error_body(response: httpx.Response) -> str:
    """Intenta extraer `detail` de un JSON de error FastAPI."""
    try:
        raw = response.read().decode(errors="replace")
        data = json.loads(raw)
        if isinstance(data, dict) and "detail" in data:
            d = data["detail"]
            if isinstance(d, str):
                return d
            if isinstance(d, list) and d:
                first = d[0]
                if isinstance(first, dict) and "msg" in first:
                    return str(first["msg"])
                return str(first)
            return str(d)
        return raw or "Error del servidor."
    except Exception:
        return "Error del servidor."
