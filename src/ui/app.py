"""Aplicación Gradio para MeetMind."""

import gradio as gr
import httpx

from src.config import get_api_base_url


def process_meeting(text: str) -> str:
    """Llama a la API para procesar el texto y devuelve el resultado formateado."""
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


def create_ui():
    """Crea la interfaz Gradio."""
    with gr.Blocks(title="MeetMind") as demo:
        gr.Markdown("# MeetMind - Procesamiento de reuniones")
        with gr.Row():
            text_input = gr.Textbox(
                label="Texto de la reunión",
                placeholder="Escribe o pega el contenido de la reunión...",
                lines=5,
            )
        with gr.Row():
            process_btn = gr.Button("Procesar", variant="primary", interactive=False)
        output = gr.Markdown(label="Resultado")

        def process_with_validation(text: str):
            if not text or not text.strip():
                return "Introduce texto antes de procesar."
            return process_meeting(text)

        process_btn.click(
            fn=process_with_validation,
            inputs=[text_input],
            outputs=[output],
            show_progress=True,
        )

        # Deshabilitar botón cuando input vacío (validación dinámica)
        def update_button(text: str):
            return gr.update(interactive=bool(text and text.strip()))

        text_input.change(fn=update_button, inputs=[text_input], outputs=[process_btn])

    return demo


demo = create_ui()

if __name__ == "__main__":
    demo.launch()
