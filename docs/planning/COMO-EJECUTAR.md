# Cómo ejecutar MeetMind

> **Entregable de US-000.** Instrucciones para ejecutar los componentes del proyecto una vez completada la estructura inicial y el Hello World end-to-end.

---

## Requisitos previos

- **Python** 3.11 o superior
- **[uv](https://docs.astral.sh/uv/)** — gestor de dependencias y entornos (instalación: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

---

## Instalación

```bash
# Clonar el repositorio (si aplica)
cd meetmind

# Instalar dependencias con uv (crea .venv automáticamente si no existe)
uv sync
# o en modo editable:
uv pip install -e .
```

---

## 1. Ejecutar la API (FastAPI)

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

- **URL base:** http://localhost:8000
- **Documentación OpenAPI:** http://localhost:8000/docs
- **Health check:**
  ```bash
  curl http://localhost:8000/health
  ```

---

## 2. Ejecutar la UI (Gradio)

```bash
uv run gradio src/ui/app.py
# o:
uv run python -m gradio src/ui/app.py
```

- La UI se abrirá en el navegador (por defecto http://localhost:7860)
- En modo demo, la UI puede invocar el grafo directamente
- Para conectar a la API: configurar `API_BASE_URL=http://localhost:8000` si la UI usa httpx

---

## 3. Ejecutar el grafo en modo standalone (desarrollo)

```bash
uv run python -c "
from src.agents.meeting.agent import get_graph
g = get_graph()
result = g.invoke({'raw_text': 'Reunión de prueba con Juan y María. Discutimos el presupuesto y las fechas.'})
print(result)
"
```

---

## 4. Flujo end-to-end (Hello World)

1. Levantar la API: `uv run uvicorn src.api.main:app --reload --port 8000`
2. Levantar la UI: `uv run gradio src/ui/app.py`
3. En la UI: escribir texto en el input → pulsar "Procesar" → ver resultado en la salida

---

## Variables de entorno (opcional)

Crear `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Variables típicas:

- `OPENAI_API_KEY` — Para modelos OpenAI (extracción, generación)
- `DATABASE_URL` — Para persistencia (SQLite por defecto: `sqlite:///./meetmind.db`)

---

*Actualizar este documento según la implementación real del proyecto.*
