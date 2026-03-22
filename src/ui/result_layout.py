"""Presentación de resultado API (spec 013): estado, avisos, análisis, transcripción.

TODO(US-009): reutilizar `split_api_payload` / `format_meta_html` desde la vista de historial
cuando exista listado lateral de reuniones en Gradio.
"""

from __future__ import annotations

import html
from typing import Any

STATUS_LABELS_ES: dict[str, str] = {
    "completed": "Completado",
    "partial": "Parcial",
    "failed": "Error",
}


def _normalize_errors(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def format_meta_html(status: str, errors: list[str]) -> str:
    """Bloque HTML: etiqueta de estado textual + lista de avisos con scroll."""
    label = html.escape(STATUS_LABELS_ES.get(status, status))
    status_block = (
        f'<div class="mm-status" role="status"><strong>Estado:</strong> <span>{label}</span></div>'
    )
    if not errors:
        warn_body = '<p class="mm-warn-empty">No hay avisos.</p>'
    else:
        items = "".join(f"<li>{html.escape(e)}</li>" for e in errors)
        warn_body = f'<div class="mm-warn-scroll"><ul class="mm-warn-list">{items}</ul></div>'
    warnings = (
        f'<section class="mm-warn" aria-label="Avisos">'
        f'<h3 class="mm-warn-title">Avisos</h3>{warn_body}</section>'
    )
    return status_block + warnings


def analysis_markdown_body(data: dict[str, Any]) -> str:
    """Solo secciones de análisis PRD (sin duplicar avisos aquí)."""
    lines = [
        "## Participantes",
        data.get("participants", "-") or "-",
        "",
        "## Temas",
        data.get("topics", "-") or "-",
        "",
        "## Acciones",
        data.get("actions", "-") or "-",
        "",
        "## Minuta",
        data.get("minutes", "-") or "-",
        "",
        "## Resumen ejecutivo",
        data.get("executive_summary", "-") or "-",
    ]
    return "\n".join(lines)


def split_api_payload(data: dict[str, Any]) -> tuple[str, str, str]:
    """
    A partir del JSON de proceso (sync o evento SSE `complete`).

    Returns:
        meta_html, analysis_markdown, transcript_text
    """
    status = data.get("status") or "completed"
    errors = _normalize_errors(data.get("processing_errors"))
    meta = format_meta_html(status, errors)
    analysis = analysis_markdown_body(data)
    tr = (data.get("transcript") or "").strip()
    return meta, analysis, tr


def render_result_as_markdown(data: dict[str, Any]) -> str:
    """Un solo Markdown (p. ej. HTTP síncrono o API externa) con estado + avisos + análisis + transcripción."""
    status = data.get("status") or "completed"
    label = STATUS_LABELS_ES.get(status, status)
    errors = _normalize_errors(data.get("processing_errors"))
    parts: list[str] = [f"## Estado: {label}", "### Avisos"]
    if not errors:
        parts.append("_No hay avisos._")
    else:
        parts.extend(f"- {e}" for e in errors)
    parts.append("")
    parts.append(analysis_markdown_body(data))
    tr = (data.get("transcript") or "").strip()
    if tr:
        parts.extend(["", "## Transcripción", tr])
    return "\n".join(parts)
