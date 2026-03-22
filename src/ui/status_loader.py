"""Mensajes y HTML del indicador de estado (loader) para multimedia y texto."""

from __future__ import annotations

import html


def loader_idle() -> str:
    """Sin proceso activo."""
    return ""


def _escape(s: str) -> str:
    return html.escape(s, quote=True)


def _transcription_mode_row(transcription_backend: str | None) -> str:
    """Fila con insignia LOCAL / NUBE / sin Whisper (solo texto)."""
    if transcription_backend == "cloud":
        return (
            '<div class="meetmind-mode-row">'
            '<span class="meetmind-mode-badge meetmind-mode-cloud">NUBE</span>'
            '<span class="meetmind-mode-desc">Transcripción con OpenAI API (whisper-1)</span>'
            "</div>"
        )
    if transcription_backend == "local":
        return (
            '<div class="meetmind-mode-row">'
            '<span class="meetmind-mode-badge meetmind-mode-local">LOCAL</span>'
            '<span class="meetmind-mode-desc">Transcripción en este servidor (openai-whisper)</span>'
            "</div>"
        )
    if transcription_backend == "none":
        return (
            '<div class="meetmind-mode-row">'
            '<span class="meetmind-mode-badge meetmind-mode-na">SIN WHISPER</span>'
            '<span class="meetmind-mode-desc">Solo análisis de texto; no hay paso de transcripción de audio</span>'
            "</div>"
        )
    return ""


def loader_custom(
    *,
    title: str,
    description: str,
    elapsed_sec: float = 0.0,
    hint: str = "",
    transcription_backend: str | None = None,
) -> str:
    """Panel genérico de carga (barra animada + título + descripción)."""
    mode_row = _transcription_mode_row(transcription_backend)
    extra = f'<p class="meetmind-loader-hint">{_escape(hint)}</p>' if hint else ""
    elapsed = f'<p class="meetmind-loader-elapsed">Tiempo transcurrido: {int(elapsed_sec)} s</p>'
    return f"""<div class="meetmind-loader">
  {mode_row}
  <div class="meetmind-loader-bar"></div>
  <p class="meetmind-loader-title">{_escape(title)}</p>
  <p class="meetmind-loader-desc">{_escape(description)}</p>
  {elapsed}
  {extra}
</div>"""


# Fases enviadas por la API (SSE) — títulos por defecto si no hay `message`
_API_PHASE_DEFAULTS: dict[str, tuple[str, str]] = {
    "received": ("Recepción", "Archivo recibido en el servidor."),
    "text_loaded": ("Texto listo", "Contenido cargado; pasando al análisis con IA."),
    "transcribing": ("Transcripción", "Convirtiendo audio o video en texto (Whisper)…"),
    "analyzing": ("Análisis", "Extrayendo participantes, temas, minuta y resumen…"),
}


def loader_from_api_phase(
    phase: str,
    message: str | None = None,
    *,
    elapsed_sec: float = 0.0,
    hint: str = "",
    transcription_backend: str | None = None,
) -> str:
    """Construye el HTML del loader a partir de un evento `phase` del servidor."""
    title, default_desc = _API_PHASE_DEFAULTS.get(phase, ("Procesando", "En curso…"))
    desc = message if message else default_desc
    return loader_custom(
        title=title,
        description=desc,
        elapsed_sec=elapsed_sec,
        hint=hint,
        transcription_backend=transcription_backend,
    )


def loader_multimedia(
    phase: int,
    *,
    elapsed_sec: float = 0.0,
    hint: str = "",
    transcription_backend: str | None = None,
) -> str:
    """
    Panel de estado para archivo multimedia.

    phase:
        0 = validación local
        1 = envío al servidor
        2 = transcripción (Whisper)
        3 = análisis IA (grafo)
    """
    phases = [
        ("Validación", "Comprobando formato y tamaño del archivo…"),
        ("Envío", "Subiendo el archivo al servidor…"),
        ("Transcripción", "Convirtiendo audio o video en texto (Whisper). Puede tardar varios minutos…"),
        ("Análisis", "Extrayendo participantes, temas, acciones, minuta y resumen ejecutivo…"),
    ]
    title, desc = phases[max(0, min(phase, len(phases) - 1))]
    return loader_custom(
        title=title,
        description=desc,
        elapsed_sec=elapsed_sec,
        hint=hint,
        transcription_backend=transcription_backend,
    )


def loader_text(*, phase: int = 0, elapsed_sec: float = 0.0) -> str:
    """Estado para procesamiento solo texto (heurística local / fallback)."""
    if phase == 0:
        desc = "Enviando texto al servidor…"
    else:
        desc = "Analizando la reunión (participantes, temas, minuta, resumen)…"
    return loader_custom(
        title="Análisis",
        description=desc,
        elapsed_sec=elapsed_sec,
        hint="",
        transcription_backend="none",
    )


def multimedia_phase_from_elapsed(elapsed_sec: float) -> int:
    """
    Avanza la fase mostrada según el tiempo (heurística: el servidor no envía progreso real).

    - 0–3 s: validación ya hecha en cliente; primer tick suele ser envío
    - 3–90 s: transcripción suele dominar
    - 90+ s: análisis / cola
    """
    if elapsed_sec < 4:
        return 1
    if elapsed_sec < 120:
        return 2
    return 3


# CSS inyectado en gr.Blocks(css=...)
LOADER_CSS = """
.meetmind-mode-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.65rem;
}
.meetmind-mode-badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
}
.meetmind-mode-desc {
  font-size: 0.82rem;
  color: var(--body-text-color-subdued, #6b7280);
}
.meetmind-mode-cloud { background: #dbeafe; color: #1d4ed8; }
.meetmind-mode-local { background: #d1fae5; color: #047857; }
.meetmind-mode-na { background: #e5e7eb; color: #4b5563; }
.meetmind-loader {
  border: 1px solid var(--border-color-primary, #e5e7eb);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 0.75rem;
  background: var(--background-fill-secondary, #f9fafb);
}
.meetmind-loader-title {
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  font-size: 1.05rem;
}
.meetmind-loader-desc, .meetmind-loader-hint, .meetmind-loader-elapsed {
  margin: 0.25rem 0 0 0;
  font-size: 0.92rem;
  color: var(--body-text-color-subdued, #6b7280);
}
.meetmind-loader-hint { font-size: 0.85rem; font-style: italic; }
.meetmind-loader-bar {
  height: 4px;
  border-radius: 2px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #3b82f6);
  background-size: 200% 100%;
  animation: meetmind-shimmer 1.2s ease-in-out infinite;
  margin-bottom: 0.75rem;
}
@keyframes meetmind-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
"""
