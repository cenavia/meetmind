"""Aplicación Gradio para MeetMind."""

from pathlib import Path

import gradio as gr
import httpx

from src.config import get_api_base_url


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
        with httpx.Client(timeout=30.0) as client:
            response = client.post(endpoint, json={"text": text.strip()})
            response.raise_for_status()
            data = response.json()
    except httpx.ConnectError:
        return "Error: No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada."
    except httpx.TimeoutException:
        return "Error: La API tardó demasiado en responder."
    except httpx.HTTPStatusError as e:
        return f"Error {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error inesperado: {e}"

    return _format_result(data)


def process_meeting_file(file) -> str:
    """Llama a la API para procesar archivo y devuelve el resultado formateado."""
    if file is None:
        return "Selecciona un archivo .txt o .md antes de procesar."

    path = file if isinstance(file, (str, Path)) else (file[0] if isinstance(file, (list, tuple)) else None)
    if not path or not Path(path).exists():
        return "Archivo no encontrado. Selecciona un archivo válido."

    api_url = get_api_base_url()
    endpoint = f"{api_url.rstrip('/')}/api/v1/process/file"

    try:
        with open(path, "rb") as f:
            files = {"file": (Path(path).name, f, "text/plain" if path.endswith(".txt") else "text/markdown")}
            with httpx.Client(timeout=30.0) as client:
                response = client.post(endpoint, files=files)
                response.raise_for_status()
                data = response.json()
    except httpx.ConnectError:
        return "Error: No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada."
    except httpx.TimeoutException:
        return "Error: La API tardó demasiado en responder."
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", e.response.text)
        except Exception:
            detail = e.response.text
        return f"Error {e.response.status_code}: {detail}"
    except Exception as e:
        return f"Error inesperado: {e}"

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
                    label="O sube un archivo (.txt o .md)",
                    file_types=[".txt", ".md"],
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
            fn=process_dispatch,
            inputs=[text_input, file_input],
            outputs=[output],
            show_progress=True,
        )

    return demo


demo = create_ui()

if __name__ == "__main__":
    demo.launch()
