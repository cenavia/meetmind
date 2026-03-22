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
:root {
  --mm-bg-main: #0b1220;
  --mm-bg-surface: #131d33;
  --mm-bg-soft: #1b2742;
  --mm-border: #2e3d63;
  --mm-text-main: #e7edff;
  --mm-text-soft: #a8b4d9;
  --mm-accent: #4f7cff;
  --mm-accent-2: #22d3ee;
  --mm-table-row: #141f36;
  --mm-table-row-alt: #1a2844;
  --mm-table-text: #eef2ff;
}
.gradio-container {
  background:
    radial-gradient(circle at 20% -10%, rgba(79,124,255,0.28), transparent 38%),
    radial-gradient(circle at 86% -16%, rgba(34,211,238,0.20), transparent 30%),
    var(--mm-bg-main);
  max-width: 100% !important;
  width: 100% !important;
}
/* Gradio centra el formulario con max-width ~640px; lo expandimos */
.gradio-container .contain,
.gradio-container .main,
.gradio-container main,
.gradio-container > div > .wrap {
  max-width: none !important;
  width: 100% !important;
}
/* Pestaña historial / columnas marcadas: todo el ancho útil */
.mm-tab-panel-full,
.mm-full-block {
  width: 100% !important;
  max-width: 100% !important;
  min-width: 0 !important;
}
.mm-tab-panel-full > *,
.mm-full-block > * {
  max-width: 100% !important;
}
/* Markdown .prose suele limitar a ~65ch */
.mm-results-stack .prose,
.mm-history-detail-md .prose,
.mm-card .prose,
.gradio-container .mm-card .prose,
.gradio-container .mm-history-detail-md .prose {
  max-width: none !important;
  width: 100% !important;
}
.mm-results-stack,
.mm-history-detail-md,
.block.mm-card,
.block.mm-history-detail-md {
  width: 100% !important;
  max-width: 100% !important;
}
.mm-results-stack .wrap,
.mm-history-detail-md .wrap,
.block.mm-card > .wrap,
.block.mm-history-detail-md > .wrap {
  width: 100% !important;
  max-width: 100% !important;
}
.mm-hero {
  border: 1px solid var(--mm-border);
  border-radius: 14px;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  background: linear-gradient(130deg, rgba(79,124,255,0.14), rgba(19,29,51,0.95));
}
.mm-kicker {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.72rem;
  color: #9bb2ff;
  font-weight: 700;
}
.mm-hero h1 {
  margin: 0.25rem 0 0.3rem 0;
  color: var(--mm-text-main);
  font-size: 1.6rem;
  line-height: 1.15;
}
.mm-subtitle {
  margin: 0;
  color: var(--mm-text-soft);
  max-width: 76ch;
}
.mm-tabs button {
  font-weight: 600 !important;
}
/* Pestañas legibles en tema oscuro (Gradio 6 suele usar role="tab") */
.mm-tabs [role="tab"] {
  color: #c4d0ef !important;
  opacity: 1 !important;
  font-weight: 600 !important;
}
.mm-tabs [role="tab"][aria-selected="false"] {
  color: #9fb0da !important;
}
.mm-tabs [role="tab"][aria-selected="true"] {
  color: #ffffff !important;
}
.mm-tabs [role="tablist"] {
  border-bottom: 1px solid var(--mm-border);
  margin-bottom: 0.75rem;
}
/* Texto de ayuda bajo inputs (Markdown sobre fondo oscuro) */
.mm-markdown-hint,
.mm-markdown-hint p,
.mm-markdown-hint em,
.mm-markdown-hint i {
  color: #c5d4f5 !important;
}
.mm-markdown-hint strong {
  color: #ffffff !important;
}
.mm-markdown-hint code,
.mm-markdown-hint .code {
  background: rgba(0, 0, 0, 0.35) !important;
  color: #e8ecff !important;
  padding: 0.1em 0.35em;
  border-radius: 4px;
}
.mm-markdown-section,
.mm-markdown-section h3,
.mm-markdown-section p {
  color: var(--mm-text-main) !important;
}
/* Controles del formulario: evitar bloques blancos sobre fondo oscuro */
.mm-input label,
.mm-input .label-wrap span,
.mm-input .block-label,
.mm-input span[data-testid="block-label"] {
  color: #f0f4ff !important;
  background: #1a2d52 !important;
  border: 1px solid #3d5a90 !important;
  box-shadow: none !important;
}
.mm-input textarea,
.mm-input input[type="text"],
.mm-input input:not([type="file"]) {
  background: var(--mm-bg-surface) !important;
  color: var(--mm-text-main) !important;
  border-color: var(--mm-border) !important;
}
.mm-input textarea::placeholder,
.mm-input input::placeholder {
  color: #c8d8f5 !important;
  opacity: 1 !important;
}
.mm-input textarea::-webkit-input-placeholder,
.mm-input input::-webkit-input-placeholder {
  color: #c8d8f5 !important;
  -webkit-text-fill-color: #c8d8f5 !important;
  opacity: 1 !important;
}
.mm-input textarea::-moz-placeholder,
.mm-input input::-moz-placeholder {
  color: #c8d8f5 !important;
  opacity: 1 !important;
}
/* Segundo bloque del formulario = subida de archivo (evita caja blanca) */
.mm-process-fields .block.mm-input + .block.mm-input .wrap,
.mm-process-fields .block.mm-input ~ .block.mm-input .wrap {
  background: var(--mm-bg-soft) !important;
  border: 1px solid var(--mm-border) !important;
  border-radius: 12px !important;
}
.mm-process-fields .block.mm-input + .block.mm-input .wrap *,
.mm-process-fields .block.mm-input ~ .block.mm-input .wrap * {
  color: var(--mm-text-main) !important;
}
.mm-process-fields .block.mm-input + .block.mm-input svg,
.mm-process-fields .block.mm-input ~ .block.mm-input svg {
  color: var(--mm-accent) !important;
  fill: var(--mm-accent) !important;
}
.mm-input .upload-container,
.mm-input [data-testid="file-upload"],
.mm-input .file-preview,
.mm-input [class*="file"] {
  background: var(--mm-bg-soft) !important;
  border-color: var(--mm-border) !important;
  color: var(--mm-text-main) !important;
}
.mm-input .upload-container *,
.mm-input [data-testid="file-upload"] * {
  color: var(--mm-text-main) !important;
}
.mm-input a,
.mm-input .upload-text {
  color: #93b4ff !important;
}
/* Acordeón técnico: barra clara ilegible → forzar panel oscuro */
#meetmind-detalles-tecnicos,
.mm-accordion-tech {
  background: transparent !important;
}
#meetmind-detalles-tecnicos > *,
.mm-accordion-tech > * {
  background: var(--mm-bg-surface) !important;
  border: 1px solid var(--mm-border) !important;
  border-radius: 10px !important;
}
#meetmind-detalles-tecnicos button,
#meetmind-detalles-tecnicos summary,
#meetmind-detalles-tecnicos .label-wrap,
#meetmind-detalles-tecnicos .panel-header,
.mm-accordion-tech button,
.mm-accordion-tech summary {
  background: #1b2742 !important;
  color: #f0f4ff !important;
  border-color: var(--mm-border) !important;
}
#meetmind-detalles-tecnicos button *,
#meetmind-detalles-tecnicos .label-wrap *,
.mm-accordion-tech button span,
.mm-accordion-tech summary * {
  color: #f0f4ff !important;
}
.mm-accordion-tech details {
  background: var(--mm-bg-surface) !important;
  border: 1px solid var(--mm-border) !important;
  border-radius: 10px !important;
}
.mm-accordion-tech summary,
.mm-accordion-tech .label-wrap {
  color: var(--mm-text-main) !important;
}
.mm-accordion-tech .prose,
.mm-accordion-tech .markdown {
  color: var(--mm-text-soft) !important;
}
/* Botones de acción */
.mm-btn-primary,
.mm-actions-row button.primary,
.gradio-container .mm-btn-primary {
  background: linear-gradient(180deg, #4568ff, #2f4ae2) !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  border: 1px solid #6b8aff !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
}
.mm-btn-primary[disabled],
.mm-actions-row button.primary[disabled] {
  color: #e8ecff !important;
  opacity: 0.5 !important;
}
.mm-btn-secondary,
.mm-history-refresh,
.gradio-container .mm-btn-secondary {
  background: var(--mm-bg-soft) !important;
  color: var(--mm-text-main) !important;
  border: 1px solid var(--mm-border) !important;
  font-weight: 600 !important;
}
.mm-btn-secondary:hover {
  background: #243558 !important;
}
/* Tabla de historial: Gradio 6 renderiza la rejilla fuera del bloque con elem_classes;
   el contenedor mm-history-df-wrap sí envuelve el componente completo. */
.mm-history-df-wrap,
.mm-history-df-wrap * {
  --cell-text-color: var(--mm-table-text);
}
.mm-history-df-wrap [role="grid"],
.mm-history-df-wrap [role="rowgroup"],
.mm-history-df-wrap .table-wrap,
.mm-history-df-wrap table {
  background: var(--mm-table-row) !important;
  color: var(--mm-table-text) !important;
  border-color: var(--mm-border) !important;
}
.mm-history-df-wrap [role="columnheader"],
.mm-history-df-wrap [role="columnheader"] *,
.mm-history-df-wrap th,
.mm-history-df-wrap th * {
  background: #0f1829 !important;
  color: #dbe4ff !important;
  border-color: var(--mm-border) !important;
  font-weight: 600 !important;
}
.mm-history-df-wrap [role="gridcell"],
.mm-history-df-wrap [role="gridcell"] *,
.mm-history-df-wrap td,
.mm-history-df-wrap td * {
  background: var(--mm-table-row) !important;
  color: var(--mm-table-text) !important;
  border-color: var(--mm-border) !important;
}
.mm-history-df-wrap [role="row"]:nth-child(even) [role="gridcell"],
.mm-history-df-wrap tr:nth-child(even) td {
  background: var(--mm-table-row-alt) !important;
}
.mm-history-df-wrap [role="row"]:nth-child(even) [role="gridcell"] * {
  background: transparent !important;
  color: var(--mm-table-text) !important;
}
/* Quitar bordes negros gruesos del componente tipo hoja de cálculo */
.mm-history-df-wrap [role="gridcell"],
.mm-history-df-wrap td {
  border-width: 1px !important;
  border-style: solid !important;
  border-color: var(--mm-border) !important;
  outline: none !important;
}
.mm-history-df-wrap input[type="search"],
.mm-history-df-wrap [data-testid="search"] input,
.mm-history-df-wrap .toolbar input {
  background: var(--mm-bg-surface) !important;
  color: var(--mm-text-main) !important;
  border: 1px solid var(--mm-border) !important;
}
.mm-history-df-wrap .label-wrap span,
.mm-history-df-wrap label {
  color: var(--mm-text-main) !important;
}
/* Respaldo si el grid sigue bajo .mm-history-table */
.mm-history-table [role="grid"],
.mm-history-table table {
  background: var(--mm-bg-surface) !important;
  color: var(--mm-text-main) !important;
}
.mm-history-table [role="columnheader"],
.mm-history-table th {
  color: var(--mm-text-soft) !important;
  background: rgba(19, 29, 51, 0.98) !important;
}
.mm-history-table [role="gridcell"],
.mm-history-table td {
  color: var(--mm-text-main) !important;
  border-color: var(--mm-border) !important;
}
/* Markdown de resultados (Análisis) */
.gradio-container .prose,
.gradio-container .markdown.prose,
.gradio-container .md,
.block.mm-card .prose {
  color: #e2e8ff !important;
}
.gradio-container .prose h1,
.gradio-container .prose h2,
.gradio-container .prose h3,
.gradio-container .prose strong {
  color: #ffffff !important;
}
.gradio-container .prose code {
  background: rgba(0, 0, 0, 0.35) !important;
  color: #f0f4ff !important;
}
/* Detalle historial: un solo Markdown (legible y con altura mínima) */
.mm-history-detail-md {
  min-height: 12rem;
  padding: 0.75rem 1rem !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}
.mm-history-detail-md .prose,
.mm-history-detail-md .markdown {
  color: #e2e8ff !important;
}
/* Pie de página Gradio */
.gradio-container footer,
.gradio-container .footer {
  color: var(--mm-text-soft) !important;
}
.gradio-container footer a {
  color: #a8c4ff !important;
}
.mm-card {
  border: 1px solid var(--mm-border);
  border-radius: 10px;
  background: linear-gradient(180deg, rgba(19,29,51,0.96), rgba(15,23,42,0.98));
}
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
  color: var(--mm-text-soft);
}
.meetmind-mode-cloud { background: #dbeafe; color: #1d4ed8; }
.meetmind-mode-local { background: #d1fae5; color: #047857; }
.meetmind-mode-na { background: #e5e7eb; color: #4b5563; }
.meetmind-loader {
  border: 1px solid var(--mm-border);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 0.75rem;
  background: linear-gradient(180deg, rgba(19,29,51,0.96), rgba(15,23,42,0.98));
}
.meetmind-loader-title {
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  font-size: 1.05rem;
  color: var(--mm-text-main);
}
.meetmind-loader-desc, .meetmind-loader-hint, .meetmind-loader-elapsed {
  margin: 0.25rem 0 0 0;
  font-size: 0.92rem;
  color: var(--mm-text-soft);
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
.mm-status {
  margin: 0.5rem 0 0.75rem 0;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  background: rgba(79, 124, 255, 0.08);
  border: 1px solid var(--mm-border);
  font-size: 0.95rem;
}
.mm-warn {
  margin-bottom: 1rem;
  border: 1px solid var(--mm-border);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  background: rgba(19, 29, 51, 0.86);
}
.mm-warn-title {
  margin: 0 0 0.4rem 0;
  font-size: 0.95rem;
  font-weight: 600;
}
.mm-warn-empty {
  margin: 0;
  font-size: 0.88rem;
  color: var(--mm-text-soft);
}
.mm-warn-scroll {
  max-height: 220px;
  overflow-y: auto;
  padding-right: 0.25rem;
}
.mm-warn-list {
  margin: 0;
  padding-left: 1.2rem;
  font-size: 0.88rem;
}
.mm-warn-list li { margin-bottom: 0.25rem; }
.mm-history-notice {
  border-radius: 9px;
  border: 1px solid var(--mm-border);
  padding: 0.65rem 0.8rem;
  margin-bottom: 0.75rem;
}
.mm-history-notice-info { background: rgba(79,124,255,0.08); color: #c8d7ff; }
.mm-history-notice-success { background: rgba(16,185,129,0.12); color: #a7f3d0; }
.mm-history-notice-error { background: rgba(239,68,68,0.12); color: #fecaca; }
.mm-history-header {
  border: 1px solid var(--mm-border);
  border-radius: 10px;
  padding: 0.75rem;
  background: linear-gradient(180deg, rgba(15,23,42,0.96), rgba(11,18,32,0.98));
  margin-bottom: 0.75rem;
}
.mm-history-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}
.mm-history-date {
  font-size: 0.82rem;
  color: var(--mm-text-soft);
}
.mm-status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.15rem 0.6rem;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.mm-badge-completed { background: rgba(16,185,129,0.18); color: #86efac; }
.mm-badge-partial { background: rgba(245,158,11,0.2); color: #fcd34d; }
.mm-badge-failed { background: rgba(239,68,68,0.2); color: #fca5a5; }
.mm-badge-unknown { background: rgba(148,163,184,0.2); color: #cbd5e1; }
.mm-history-header-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}
.mm-history-key {
  display: inline-block;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.68rem;
  color: #91a3d6;
  margin-bottom: 0.22rem;
}
.mm-history-header-grid p {
  margin: 0;
  color: var(--mm-text-main);
  font-size: 0.86rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
@media (max-width: 980px) {
  .mm-history-header-grid {
    grid-template-columns: 1fr;
  }
}
"""
