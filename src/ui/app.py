"""Aplicación Gradio para MeetMind."""

from pathlib import Path

import gradio as gr
import httpx

from src.config import get_api_base_url
from src.ui.utils import get_mime_for_extension, validate_file


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
    """Formatea el resultado estructurado como Markdown."""
    lines = [
        "## Participantes",
        data.get("participants", "-"),
        "",
        "## Temas",
        data.get("topics", "-"),
        "",
        "## Acciones",
        data.get("actions", "-"),
        "",
        "## Minuta",
        data.get("minutes", "-"),
        "",
        "## Resumen ejecutivo",
        data.get("executive_summary", "-"),
    ]
    return "\n".join(lines)


def process_meeting_text(text: str) -> str:
    """Llama a la API para procesar texto y devuelve el resultado formateado."""
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


def process_meeting_file(file) -> str:
    """Llama a la API para procesar archivo y devuelve el resultado formateado."""
    if file is None:
        return "Selecciona un archivo antes de procesar."

    path = file if isinstance(file, (str, Path)) else (file[0] if isinstance(file, (list, tuple)) else None)
    if not path or not Path(path).exists():
        return "Archivo no encontrado. Selecciona un archivo válido."

    err = validate_file(path)
    if err:
        return err

    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/file"
    mime = get_mime_for_extension(Path(path).name)

    try:
        with open(path, "rb") as f:
            files = {"file": (Path(path).name, f, mime)}
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


def process_dispatch(text: str, file) -> str:
    """Procesa según el modo activo: texto o archivo."""
    if file is not None:
        path = file if isinstance(file, (str, Path)) else (file[0] if isinstance(file, (list, tuple)) else None)
        if path and Path(str(path)).exists():
            return process_meeting_file(file)
    if text and text.strip():
        return process_meeting_text(text)
    return "Introduce texto o sube un archivo antes de procesar."


def on_process(text: str, file) -> tuple[str, dict]:
    """Wrapper que procesa y desactiva el botón Procesar inmediatamente (FR-005, FR-006)."""
    result = process_dispatch(text, file)
    return result, gr.update(interactive=False)


def _has_file(file) -> bool:
    """Comprueba si hay archivo seleccionado."""
    if file is None:
        return False
    path = file if isinstance(file, (str, Path)) else (file[0] if isinstance(file, (list, tuple)) else None)
    return path is not None and Path(str(path)).exists()


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
    with gr.Blocks(title="MeetMind") as demo:
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
        gr.Markdown("*Elige uno: texto o archivo. Para cambiar de modo, pulsa Limpiar.*")
        with gr.Row():
            process_btn = gr.Button("Procesar", variant="primary", interactive=False)
            clear_btn = gr.Button("Limpiar", variant="secondary")
        output = gr.Markdown(label="Resultado")

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
                "",
            )

        clear_btn.click(
            fn=do_clear,
            inputs=[],
            outputs=[text_input, file_input, process_btn, output],
        )

        process_btn.click(
            fn=on_process,
            inputs=[text_input, file_input],
            outputs=[output, process_btn],
            show_progress=True,  # Loader visible durante procesamiento (US-004)
        )

    return demo


demo = create_ui()

if __name__ == "__main__":
    demo.launch()
