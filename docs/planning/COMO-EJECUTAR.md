# Cómo ejecutar MeetMind

> **Entregable de US-000.** Instrucciones para ejecutar los componentes del proyecto una vez completada la estructura inicial y el Hello World end-to-end.

---

## Requisitos previos

- **Python** 3.11 o superior
- **[uv](https://docs.astral.sh/uv/)** — gestor de dependencias y entornos (instalación: `curl -LsSf https://astral.sh/uv/install.sh | sh`)

---

## Instalación

```bash
cd meetmind
uv sync
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
  # {"status":"ok"}
  ```

---

## 2. Ejecutar la UI (Gradio)

En otra terminal:

```bash
# URL por defecto (localhost:8000)
uv run gradio src/ui/app.py

# O con API en otra URL:
API_BASE_URL=http://localhost:8000 uv run gradio src/ui/app.py
```

- La UI se abrirá en el navegador (por defecto http://localhost:7860)
- La UI invoca la API por HTTP usando `API_BASE_URL`

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

1. Levantar la API: `uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
2. Levantar la UI: `uv run gradio src/ui/app.py`
3. En la UI: escribir texto en el input → pulsar **Procesar** → ver resultado estructurado (participantes, temas, acciones, minuta, resumen)

### 4.1. Flujo con archivo (TXT o Markdown)

- En la misma pantalla: área de texto **o** selector de archivo (.txt, .md)
- Subir archivo: arrastrar o seleccionar → pulsar **Procesar** → ver resultado
- Para cambiar de modo (texto ↔ archivo): pulsar **Limpiar**

---

## 5. Probar la API directamente

**Texto:**
```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión de prueba con Juan y María."}'
```

**Archivo (.txt o .md):**
```bash
curl -X POST http://localhost:8000/api/v1/process/file \
  -F "file=@notas_reunion.txt"
```

---

## Variables de entorno

Crear `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

| Variable       | Default              | Descripción                          |
|----------------|----------------------|--------------------------------------|
| API_BASE_URL   | http://localhost:8000| URL base de la API (usado por la UI) |
| OPENAI_API_KEY | —                    | No requerido en Hello World (modo mock) |
| DATABASE_URL   | —                    | Para futuras fases (persistencia)    |

---

## Solución de problemas

- **La UI no conecta con la API**: Comprobar que la API está en marcha y que `API_BASE_URL` apunta al host/puerto correctos.
- **ModuleNotFoundError**: Ejecutar `uv sync` de nuevo.
- **Puerto en uso**: Cambiar `--port` en uvicorn o la configuración de Gradio.

---

*Actualizado según implementación del Hello World E2E (US-000) y procesamiento de archivos TXT/MD (US-002).*
