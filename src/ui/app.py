"""Aplicación Gradio para MeetMind."""

from __future__ import annotations

import html
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from uuid import UUID

import gradio as gr
import httpx

from src.config import (
    get_api_base_url,
    get_processing_timeout_sec,
    get_transcription_backend,
)
from src.ui.sse_client import iter_sse_events, read_http_error_body
from src.ui.result_layout import STATUS_LABELS_ES, render_result_as_markdown, split_api_payload
from src.ui.status_loader import (
    LOADER_CSS,
    loader_from_api_phase,
    loader_idle,
    loader_multimedia,
)
from src.ui.theme import meetmind_theme
from src.ui.utils import get_mime_for_extension, is_multimedia_path, validate_file


def _format_http_error(e: httpx.HTTPStatusError) -> str:
    """Formatea error HTTP con mensaje amigable, sin exponer detalles técnicos."""
    try:
        body = e.response.json()
        if isinstance(body, dict) and "detail" in body:
            detail = body["detail"]
            if isinstance(detail, str):
                return detail
            if isinstance(detail, list) and detail:
                first = detail[0]
                if isinstance(first, dict) and "msg" in first:
                    return first["msg"]
                return str(first)
    except Exception:
        pass
    return "Ha ocurrido un error con el servicio. Intenta de nuevo más tarde."


def _format_result(data: dict) -> str:
    """Resultado completo en Markdown (HTTP síncrono y compatibilidad)."""
    return render_result_as_markdown(data)


def _technical_details_markdown() -> str:
    from src.config import get_transcription_mode_label, get_processing_timeout_sec

    m = max(1, (get_processing_timeout_sec() + 59) // 60)
    return (
        f"**Modo de transcripción (servidor):** {get_transcription_mode_label()}\n\n"
        f"**Tiempo máximo de espera:** ~{m} min.\n\n"
        "_No se muestran claves API, URLs de base de datos ni rutas internas._"
    )


def _event_transcription_backend(event: dict, *, is_multimedia_file: bool) -> str | None:
    """Campo `transcription_backend` del SSE o inferencia (API antigua)."""
    tb = event.get("transcription_backend")
    if tb in ("cloud", "local", "none"):
        return tb
    if is_multimedia_file:
        return get_transcription_backend()
    return "none"


def _timeout_hint_minutes() -> str:
    sec = get_processing_timeout_sec()
    m = max(1, (sec + 59) // 60)
    return f"Tiempo máximo de espera configurado: ~{m} min."


def _resolve_file_path(file) -> Path | None:
    if file is None:
        return None
    raw = file if isinstance(file, (str, Path)) else (file[0] if isinstance(file, (list, tuple)) else None)
    if not raw:
        return None
    return Path(str(raw))


def process_meeting_text(text: str) -> str:
    """Llama a la API para procesar texto (sin streaming; uso externo)."""
    if not text or not text.strip():
        return "Por favor, introduce texto de la reunión antes de procesar."

    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/text"

    try:
        with httpx.Client(timeout=600.0) as client:
            response = client.post(endpoint, json={"text": text.strip()})
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError:
        return "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada."
    except httpx.TimeoutException:
        return "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto."
    except httpx.HTTPStatusError as e:
        return _format_http_error(e)
    except Exception:
        return "Ha ocurrido un error. Intenta de nuevo."

    return _format_result(data)


def _http_process_file(path: Path) -> str:
    """POST /process/file (sin SSE); respaldo si no hubiera stream."""
    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/file"
    mime = get_mime_for_extension(path.name)

    try:
        with open(path, "rb") as f:
            files = {"file": (path.name, f, mime)}
            with httpx.Client(timeout=600.0) as client:
                response = client.post(endpoint, files=files)
                response.raise_for_status()
                data = response.json()
    except httpx.ConnectError:
        return "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada."
    except httpx.TimeoutException:
        return "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto."
    except httpx.HTTPStatusError as e:
        return _format_http_error(e)
    except Exception:
        return "Ha ocurrido un error. Intenta de nuevo."

    return _format_result(data)


def _sse_file_worker(path: Path, q: queue.Queue) -> None:
    """Lee POST /file/stream y encola cada evento JSON; termina con None."""
    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/file/stream"
    mime = get_mime_for_extension(path.name)
    try:
        with httpx.Client(timeout=600.0) as client:
            with open(path, "rb") as f:
                files = {"file": (path.name, f, mime)}
                with client.stream("POST", endpoint, files=files) as response:
                    if response.status_code != 200:
                        q.put(
                            {
                                "type": "error",
                                "detail": read_http_error_body(response),
                            }
                        )
                        q.put(None)
                        return
                    for event in iter_sse_events(response):
                        q.put(event)
                    q.put(None)
    except httpx.ConnectError:
        q.put(
            {
                "type": "error",
                "detail": "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada.",
            }
        )
        q.put(None)
    except httpx.TimeoutException:
        q.put(
            {
                "type": "error",
                "detail": "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto.",
            }
        )
        q.put(None)
    except Exception:
        q.put({"type": "error", "detail": "Ha ocurrido un error. Intenta de nuevo."})
        q.put(None)


def _sse_text_worker(text: str, q: queue.Queue) -> None:
    """Lee POST /text/stream."""
    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/text/stream"
    try:
        with httpx.Client(timeout=600.0) as client:
            with client.stream("POST", endpoint, json={"text": text.strip()}) as response:
                if response.status_code != 200:
                    q.put({"type": "error", "detail": read_http_error_body(response)})
                    q.put(None)
                    return
                for event in iter_sse_events(response):
                    q.put(event)
                q.put(None)
    except httpx.ConnectError:
        q.put(
            {
                "type": "error",
                "detail": "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada.",
            }
        )
        q.put(None)
    except httpx.TimeoutException:
        q.put(
            {
                "type": "error",
                "detail": "El procesamiento tardó demasiado. Intenta de nuevo o usa un texto más corto.",
            }
        )
        q.put(None)
    except Exception:
        q.put({"type": "error", "detail": "Ha ocurrido un error. Intenta de nuevo."})
        q.put(None)


def process_meeting_file(file) -> str:
    """Llama a la API para procesar archivo (validación + envío)."""
    if file is None:
        return "Selecciona un archivo antes de procesar."

    path = _resolve_file_path(file)
    if not path or not path.exists():
        return "Archivo no encontrado. Selecciona un archivo válido."

    err = validate_file(path)
    if err:
        return err

    return _http_process_file(path)


def on_process(text: str, file):
    """
    Procesa texto o archivo con panel de estado alineado a las **fases reales** del servidor (SSE).
    Salidas: loader, meta (estado+avisos HTML), análisis Markdown, transcripción, botón procesar.
    """
    done_btn = gr.update(interactive=False)
    tr_empty = gr.update(value="", visible=False)
    meta_empty = gr.update(value="")
    path = _resolve_file_path(file)

    def _yield_idle(meta_h: str, analysis: str, tr_upd, btn):
        yield (
            gr.update(value=loader_idle()),
            gr.update(value=meta_h),
            gr.update(value=analysis),
            tr_upd,
            btn,
        )

    if path and path.exists():
        err = validate_file(path)
        if err:
            yield from _yield_idle(
                "",
                f"## Validación\n\n{err}",
                tr_empty,
                gr.update(interactive=True),
            )
            return

        is_mm = is_multimedia_path(path)
        hint = _timeout_hint_minutes()
        tb_initial: str | None = get_transcription_backend() if is_mm else "none"

        yield (
            gr.update(
                value=loader_multimedia(1, hint=hint, transcription_backend=tb_initial),
            ),
            meta_empty,
            gr.update(value=""),
            tr_empty,
            done_btn,
        )

        q: queue.Queue = queue.Queue()
        threading.Thread(target=_sse_file_worker, args=(path, q), daemon=True).start()

        result_meta = ""
        result_analysis = ""
        result_tr = tr_empty
        t0 = time.monotonic()
        while True:
            try:
                event = q.get(timeout=0.5)
            except queue.Empty:
                continue
            if event is None:
                break
            et = event.get("type")
            elapsed = time.monotonic() - t0
            if et == "phase":
                panel = loader_from_api_phase(
                    event.get("phase", ""),
                    event.get("message"),
                    elapsed_sec=elapsed,
                    hint=hint,
                    transcription_backend=_event_transcription_backend(event, is_multimedia_file=is_mm),
                )
                yield (
                    gr.update(value=panel),
                    meta_empty,
                    gr.update(value=""),
                    tr_empty,
                    done_btn,
                )
            elif et == "complete":
                m, a, tr_txt = split_api_payload(event["data"])
                result_meta = m
                result_analysis = a
                result_tr = gr.update(value=tr_txt, visible=bool(tr_txt))
            elif et == "error":
                detail = event.get("detail", "Error")
                msg = detail if isinstance(detail, str) else str(detail)
                result_meta = ""
                result_analysis = f"## Error\n\n{msg}"
                result_tr = tr_empty

        if not result_analysis:
            result_analysis = "Respuesta incompleta del servidor."

        yield (
            gr.update(value=loader_idle()),
            gr.update(value=result_meta),
            gr.update(value=result_analysis),
            result_tr,
            gr.update(interactive=True),
        )
        return

    if text and text.strip():
        yield (
            gr.update(
                value=loader_from_api_phase(
                    "analyzing",
                    "Enviando texto al servidor…",
                    hint=_timeout_hint_minutes(),
                    transcription_backend="none",
                )
            ),
            meta_empty,
            gr.update(value=""),
            tr_empty,
            done_btn,
        )

        q2: queue.Queue = queue.Queue()
        threading.Thread(target=_sse_text_worker, args=(text, q2), daemon=True).start()

        hint_txt = _timeout_hint_minutes()
        result_meta = ""
        result_analysis = ""
        result_tr = tr_empty
        t0 = time.monotonic()
        while True:
            try:
                event = q2.get(timeout=0.5)
            except queue.Empty:
                continue
            if event is None:
                break
            et = event.get("type")
            elapsed = time.monotonic() - t0
            if et == "phase":
                panel = loader_from_api_phase(
                    event.get("phase", ""),
                    event.get("message"),
                    elapsed_sec=elapsed,
                    hint=hint_txt,
                    transcription_backend=_event_transcription_backend(event, is_multimedia_file=False),
                )
                yield (
                    gr.update(value=panel),
                    meta_empty,
                    gr.update(value=""),
                    tr_empty,
                    done_btn,
                )
            elif et == "complete":
                m, a, tr_txt = split_api_payload(event["data"])
                result_meta = m
                result_analysis = a
                result_tr = gr.update(value=tr_txt, visible=bool(tr_txt))
            elif et == "error":
                detail = event.get("detail", "Error")
                msg = detail if isinstance(detail, str) else str(detail)
                result_meta = ""
                result_analysis = f"## Error\n\n{msg}"
                result_tr = tr_empty

        if not result_analysis:
            result_analysis = "Respuesta incompleta del servidor."

        yield (
            gr.update(value=loader_idle()),
            gr.update(value=result_meta),
            gr.update(value=result_analysis),
            result_tr,
            gr.update(interactive=True),
        )
        return

    yield (
        gr.update(value=loader_idle()),
        meta_empty,
        gr.update(
            value=(
                "## Falta contenido\n\nAñade **texto de la reunión** o **un archivo** "
                "antes de pulsar **Procesar**."
            )
        ),
        tr_empty,
        gr.update(interactive=True),
    )


def _has_file(file) -> bool:
    """Comprueba si hay archivo seleccionado."""
    if file is None:
        return False
    path = _resolve_file_path(file)
    return path is not None and path.exists()


def _has_text(text: str) -> bool:
    """Comprueba si hay texto con contenido."""
    return bool(text and text.strip())


def update_inputs(text: str, file) -> tuple[dict, dict, dict]:
    """Actualiza el estado de los inputs y del botón según bloqueo mutuo."""
    has_t = _has_text(text)
    has_f = _has_file(file)
    can_process = has_t or has_f
    return (
        gr.update(interactive=not has_f),  # text_input: bloqueado si hay archivo
        gr.update(interactive=not has_t),  # file_input: bloqueado si hay texto
        gr.update(interactive=can_process),  # process_btn
    )


def _parse_created_at(value: str | None) -> str:
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%d %b %Y · %H:%M")
    except Exception:
        return value


def _history_detail_markdown(item: dict) -> str:
    """Detalle completo para historial: metadatos persistidos + mismo cuerpo que el flujo principal."""
    created = _parse_created_at(item.get("created_at"))
    src = item.get("source_file_name") or "Texto pegado"
    st = item.get("source_file_type") or "n/a"
    rid = str(item.get("id") or "")
    head = (
        "### Metadatos\n\n"
        f"- **Fecha:** {created}\n"
        f"- **Origen:** {src}\n"
        f"- **Tipo:** {st}\n"
        f"- **ID:** `{rid}`\n\n"
        "---\n\n"
    )
    return head + render_result_as_markdown(item)


def _history_notice(message: str, tone: str = "info") -> str:
    safe_message = html.escape(message)
    return f'<div class="mm-history-notice mm-history-notice-{tone}">{safe_message}</div>'


def _history_option_label(item: dict) -> str:
    created = _parse_created_at(item.get("created_at"))
    status = STATUS_LABELS_ES.get(item.get("status", ""), item.get("status", "Sin estado"))
    source = item.get("source_file_name") or "Texto pegado"
    return f"{created} · {status} · {source}"


def _history_empty_detail_markdown() -> dict:
    """Limpia el bloque único de detalle (evita fallos de Gradio al actualizar varios hijos + Column.visible)."""
    return gr.update(value="")


def _coerce_meeting_id(value) -> str | None:
    """Normaliza a UUID string válido para la ruta GET /meetings/{id}."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return str(UUID(s))
    except ValueError:
        return None


def _resolve_meeting_id_from_select(evt: gr.SelectData, history_row_ids: list[str] | None) -> str | None:
    """
    Gradio 6 a veces no rellena `row_value` en Dataframe, o la última celda no es el UUID.
    Orden: (1) buscar UUID en celdas de la fila, (2) índice de fila + lista sincronizada al cargar tabla.
    """
    rv = evt.row_value
    if isinstance(rv, (list, tuple)):
        for cell in reversed(rv):
            mid = _coerce_meeting_id(cell)
            if mid:
                return mid
    ids = history_row_ids if isinstance(history_row_ids, list) else []
    if ids:
        idx = evt.index
        row_i = idx[0] if isinstance(idx, (list, tuple)) else idx
        if isinstance(row_i, int) and 0 <= row_i < len(ids):
            return _coerce_meeting_id(ids[row_i])
    return None


def _fetch_meeting_detail(meeting_id: str) -> tuple[dict | None, str | None]:
    endpoint = f"{get_api_base_url().rstrip('/')}/api/v1/meetings/{meeting_id}"
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(endpoint)
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError:
        return None, "No se pudo conectar con la API para leer el detalle."
    except httpx.TimeoutException:
        return None, "La API tardó demasiado en responder al leer el detalle."
    except httpx.HTTPStatusError as e:
        return None, _format_http_error(e)
    except Exception:
        return None, "No se pudo cargar el detalle de la reunión."
    if not isinstance(data, dict):
        return None, "La respuesta de detalle no tiene formato válido."
    return data, None


def _history_table_rows(items: list[dict]) -> tuple[list[list[str]], list[str]]:
    """Filas para la tabla + IDs en el mismo orden (respaldo si `row_value` falla en el cliente)."""
    rows: list[list[str]] = []
    ids: list[str] = []
    for item in items:
        meeting_id = _coerce_meeting_id(item.get("id"))
        if not meeting_id:
            continue
        created = _parse_created_at(item.get("created_at"))
        status_raw = str(item.get("status") or "")
        status = STATUS_LABELS_ES.get(status_raw, status_raw or "Sin estado")
        source = str(item.get("source_file_name") or "Texto pegado")
        source_type = str(item.get("source_file_type") or "n/a")
        rows.append([created, status, source, source_type, meeting_id])
        ids.append(meeting_id)
    return rows, ids


def load_meeting_history() -> tuple[dict, dict, dict, dict, dict, list[str]]:
    endpoint = f"{get_api_base_url().rstrip('/')}/api/v1/meetings"
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(endpoint)
            response.raise_for_status()
            payload = response.json()
    except httpx.ConnectError:
        return (
            gr.update(value=_history_notice("No se pudo conectar con la API para leer el historial.", "error")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )
    except httpx.TimeoutException:
        return (
            gr.update(value=_history_notice("La API tardó demasiado en responder al cargar historial.", "error")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )
    except httpx.HTTPStatusError as e:
        return (
            gr.update(value=_history_notice(_format_http_error(e), "error")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )
    except Exception:
        return (
            gr.update(value=_history_notice("No se pudo cargar el historial en este momento.", "error")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )

    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        return (
            gr.update(value=_history_notice("Aun no hay reuniones procesadas guardadas.", "info")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )

    rows, row_ids = _history_table_rows(items)
    if not rows:
        return (
            gr.update(value=_history_notice("No se pudo preparar la tabla de reuniones.", "error")),
            gr.update(value=[]),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
            [],
        )

    return (
        gr.update(value=_history_notice(f"Se cargaron {len(rows)} reuniones. Haz clic en una fila para ver detalle.", "success")),
        gr.update(value=rows),
        gr.update(visible=True),
        gr.update(visible=False),
        _history_empty_detail_markdown(),
        row_ids,
    )


def on_history_row_select(evt: gr.SelectData, history_row_ids: list[str]):
    """Resuelve el UUID de la fila y llama GET /api/v1/meetings/{id} contra la API (BD vía FastAPI)."""
    meeting_id = _resolve_meeting_id_from_select(evt, history_row_ids)
    if not meeting_id:
        return (
            gr.update(
                value=_history_notice(
                    "No se pudo identificar la reunión desde la tabla. Pulsa «Actualizar historial» y vuelve a elegir la fila.",
                    "error",
                )
            ),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
        )

    item, err = _fetch_meeting_detail(meeting_id)
    if err or item is None:
        return (
            gr.update(value=_history_notice(err or "No se pudo leer el detalle.", "error")),
            gr.update(visible=True),
            gr.update(visible=False),
            _history_empty_detail_markdown(),
        )

    detail_md = _history_detail_markdown(item)
    return (
        gr.update(value=_history_notice("Detalle cargado correctamente.", "success")),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(value=detail_md),
    )


def back_to_history_list():
    return (
        gr.update(value=_history_notice("Selecciona otra reunión de la tabla.", "info")),
        gr.update(visible=True),
        gr.update(visible=False),
        _history_empty_detail_markdown(),
    )


def on_main_tabs_select(evt: gr.SelectData):
    """Al entrar en Historial, carga la lista (Gradio 6: `Tabs.select` es más fiable que depender solo del tab hijo)."""
    v = str(evt.value).strip().lower()
    if v in ("historial", "history"):
        return load_meeting_history()
    return tuple(gr.skip() for _ in range(6))


def create_ui():
    """Crea la interfaz Gradio."""
    with gr.Blocks(
        title="MeetMind",
        theme=meetmind_theme(),
        css=LOADER_CSS,
        fill_width=True,
    ) as demo:
        gr.HTML(
            """
            <header class="mm-hero">
              <p class="mm-kicker">MeetMind</p>
              <h1>Procesamiento y seguimiento de reuniones</h1>
              <p class="mm-subtitle">
                Procesa contenido nuevo y consulta ejecuciones anteriores con un detalle consistente
                de estado, avisos y resultado analítico.
              </p>
            </header>
            """
        )

        history_row_ids = gr.State([])

        with gr.Tabs(elem_classes=["mm-tabs"]) as main_tabs:
            with gr.Tab("Procesar reunion", id="process"):
                with gr.Row():
                    with gr.Column(scale=1, elem_classes=["mm-process-fields", "mm-full-block"]):
                        text_input = gr.Textbox(
                            label="Texto de la reunion",
                            placeholder="Escribe o pega el contenido de la reunion...",
                            lines=6,
                            elem_classes=["mm-input"],
                        )
                        file_input = gr.File(
                            label="O sube un archivo (TXT, MD, MP4, MOV, MP3, WAV, M4A)",
                            file_types=[".txt", ".md", ".mp4", ".mov", ".mp3", ".wav", ".m4a"],
                            type="filepath",
                            elem_classes=["mm-input"],
                        )
                gr.Markdown(
                    "*Elige uno: texto o archivo. Para cambiar de modo, pulsa Limpiar.*",
                    elem_classes=["mm-markdown-hint"],
                )
                status_panel = gr.HTML(value="")
                with gr.Accordion(
                    "Detalles tecnicos",
                    open=False,
                    elem_id="meetmind-detalles-tecnicos",
                    elem_classes=["mm-accordion-tech"],
                ):
                    gr.Markdown(_technical_details_markdown())
                with gr.Column(elem_classes=["mm-results-stack", "mm-full-block"]):
                    result_meta = gr.HTML(value="", elem_classes=["mm-card"])
                    output = gr.Markdown(label="Analisis", elem_classes=["mm-card"])
                    try:
                        transcript_tb = gr.Textbox(
                            label="Transcripcion",
                            lines=12,
                            max_lines=24,
                            interactive=False,
                            visible=False,
                            show_copy_button=True,
                            elem_classes=["mm-card"],
                        )
                    except TypeError:
                        transcript_tb = gr.Textbox(
                            label="Transcripcion",
                            lines=12,
                            max_lines=24,
                            interactive=False,
                            visible=False,
                            elem_classes=["mm-card"],
                        )
                with gr.Row(elem_classes=["mm-actions-row"]):
                    process_btn = gr.Button(
                        "Procesar",
                        variant="primary",
                        interactive=False,
                        elem_classes=["mm-btn-primary"],
                    )
                    clear_btn = gr.Button(
                        "Limpiar",
                        variant="secondary",
                        elem_classes=["mm-btn-secondary"],
                    )

            with gr.Tab(
                "Historial",
                id="history",
                render_children=True,
                elem_classes=["mm-tab-panel-full"],
            ):
                gr.Markdown(
                    "### Reuniones procesadas\n"
                    "Haz clic sobre una fila para abrir la vista de detalle.",
                    elem_classes=["mm-markdown-section"],
                )
                history_info = gr.HTML(value=_history_notice("Pulsa \"Actualizar historial\" para cargar datos.", "info"))
                with gr.Column(visible=True, elem_classes=["mm-full-block"]) as history_list_view:
                    history_refresh_btn = gr.Button(
                        "Actualizar historial",
                        variant="secondary",
                        elem_classes=["mm-btn-secondary", "mm-history-refresh"],
                    )
                    with gr.Column(elem_classes=["mm-history-df-wrap"]):
                        history_table = gr.Dataframe(
                            headers=["Fecha", "Estado", "Origen", "Tipo", "ID reunión"],
                            datatype=["str", "str", "str", "str", "str"],
                            value=[],
                            interactive=True,
                            static_columns=[0, 1, 2, 3, 4],
                            max_height=420,
                            show_search="search",
                            label="Tabla de reuniones procesadas",
                            elem_classes=["mm-history-table"],
                        )
                with gr.Column(visible=False, elem_classes=["mm-full-block"]) as history_detail_view:
                    history_back_btn = gr.Button(
                        "Volver al listado",
                        variant="secondary",
                        elem_classes=["mm-btn-secondary"],
                    )
                    history_detail_md = gr.Markdown(
                        label="Detalle de la reunion",
                        value="",
                        elem_classes=["mm-card", "mm-history-detail-md"],
                    )

        def on_text_change(text: str, file):
            return update_inputs(text, file)

        def on_file_change(text: str, file):
            return update_inputs(text, file)

        text_input.change(
            fn=on_text_change,
            inputs=[text_input, file_input],
            outputs=[text_input, file_input, process_btn],
        )
        file_input.change(
            fn=on_file_change,
            inputs=[text_input, file_input],
            outputs=[text_input, file_input, process_btn],
        )

        def do_clear():
            return (
                gr.update(value="", interactive=True),
                gr.update(value=None, interactive=True),
                gr.update(interactive=False),
                gr.update(value=""),
                "",
                "",
                gr.update(value="", visible=False),
            )

        clear_btn.click(
            fn=do_clear,
            inputs=[],
            outputs=[
                text_input,
                file_input,
                process_btn,
                status_panel,
                result_meta,
                output,
                transcript_tb,
            ],
        )

        process_btn.click(
            fn=on_process,
            inputs=[text_input, file_input],
            outputs=[status_panel, result_meta, output, transcript_tb, process_btn],
            show_progress=True,
        )

        history_refresh_btn.click(
            fn=load_meeting_history,
            inputs=[],
            outputs=[
                history_info,
                history_table,
                history_list_view,
                history_detail_view,
                history_detail_md,
                history_row_ids,
            ],
        )
        main_tabs.select(
            fn=on_main_tabs_select,
            inputs=[],
            outputs=[
                history_info,
                history_table,
                history_list_view,
                history_detail_view,
                history_detail_md,
                history_row_ids,
            ],
        )
        history_table.select(
            fn=on_history_row_select,
            inputs=[history_row_ids],
            outputs=[
                history_info,
                history_list_view,
                history_detail_view,
                history_detail_md,
            ],
        )
        history_back_btn.click(
            fn=back_to_history_list,
            inputs=[],
            outputs=[
                history_info,
                history_list_view,
                history_detail_view,
                history_detail_md,
            ],
        )

    return demo


demo = create_ui()

if __name__ == "__main__":
    demo.launch()
