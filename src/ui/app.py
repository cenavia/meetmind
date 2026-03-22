"""Aplicación Gradio para MeetMind."""

from __future__ import annotations

import queue
import threading
import time
from pathlib import Path

import gradio as gr
import httpx

from src.config import (
    get_api_base_url,
    get_processing_timeout_sec,
    get_transcription_backend,
)
from src.ui.sse_client import iter_sse_events, read_http_error_body
from src.ui.result_layout import render_result_as_markdown, split_api_payload
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


def create_ui():
    """Crea la interfaz Gradio."""
    with gr.Blocks(title="MeetMind", theme=meetmind_theme(), css=LOADER_CSS) as demo:
        gr.Markdown("# MeetMind - Procesamiento de reuniones")
        with gr.Row():
            with gr.Column(scale=1):
                text_input = gr.Textbox(
                    label="Texto de la reunión",
                    placeholder="Escribe o pega el contenido de la reunión...",
                    lines=5,
                )
                file_input = gr.File(
                    label="O sube un archivo (TXT, MD, MP4, MOV, MP3, WAV, M4A)",
                    file_types=[".txt", ".md", ".mp4", ".mov", ".mp3", ".wav", ".m4a"],
                    type="filepath",
                )
        gr.Markdown(
            "*Elige uno: texto o archivo. Para cambiar de modo, pulsa Limpiar. "
            "Durante el procesamiento verás **NUBE** o **LOCAL** según dónde corre Whisper "
            "(configuración `TRANSCRIPTION_BACKEND` / `OPENAI_API_KEY` en el servidor).*"
        )
        status_panel = gr.HTML(value="")
        with gr.Accordion("Detalles técnicos", open=False):
            gr.Markdown(_technical_details_markdown())
        with gr.Row():
            with gr.Column(scale=3):
                result_meta = gr.HTML(value="")
                output = gr.Markdown(label="Análisis")
            with gr.Column(scale=2):
                try:
                    transcript_tb = gr.Textbox(
                        label="Transcripción",
                        lines=12,
                        max_lines=24,
                        interactive=False,
                        visible=False,
                        show_copy_button=True,
                    )
                except TypeError:
                    transcript_tb = gr.Textbox(
                        label="Transcripción",
                        lines=12,
                        max_lines=24,
                        interactive=False,
                        visible=False,
                    )
        with gr.Row():
            process_btn = gr.Button("Procesar", variant="primary", interactive=False)
            clear_btn = gr.Button("Limpiar", variant="secondary")

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

    return demo


demo = create_ui()

if __name__ == "__main__":
    demo.launch()
