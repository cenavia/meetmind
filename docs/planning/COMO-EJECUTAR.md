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
| DATABASE_URL   | sqlite:///./meetmind.db | SQLite en el directorio de trabajo de la API; persistencia de reuniones procesadas (GET `/api/v1/meetings`) |

**Historial persistido (tras procesar texto o archivo):**

```bash
curl -s http://localhost:8000/api/v1/meetings
```

---

## 6. Ejecutar con Docker

```bash
docker build -t meetmind:hf .
docker run -p 7860:7860 --env-file .env meetmind:hf
```

- La API (puerto 8000) y la UI (puerto 7860) corren en el mismo contenedor.
- Dentro del contenedor, la UI usa `API_BASE_URL=http://localhost:8000` para conectar con la API.
- Si usas `--env-file .env` con `DATABASE_URL=sqlite:///./meetmind.db`, la imagen garantiza permisos de escritura en el directorio de trabajo.
- Para Hugging Face Spaces (sin `.env`), la imagen usa por defecto `DATABASE_URL=sqlite:////tmp/meetmind.db`.

### 6.1. Rendimiento con multimedia (Whisper local)

| Técnica | Qué hace |
|--------|-----------|
| **Precarga en build** | Durante `docker build` se descarga el modelo indicado (por defecto `small`) y se copia a `/home/user/.cache/whisper`, evitando la descarga en el primer request. |
| **Hilos CPU** | El entrypoint define `OMP_NUM_THREADS` (y afines) con `nproc` para usar todos los cores del contenedor. Opcional: `TORCH_NUM_THREADS` o `OMP_NUM_THREADS` en el entorno para fijar un valor. |
| **Modelo más ligero** | `docker build --build-arg WHISPER_DOCKER_MODEL=base -t meetmind:hf .` y `TRANSCRIPTION_MODEL=base` en `.env` (más rápido en CPU, algo menos de precisión). |
| **Nube** | `TRANSCRIPTION_BACKEND=cloud` + `OPENAI_API_KEY`: suele ser más rápido que CPU local si el archivo entra en ~25 MB. |

---

## Solución de problemas

- **La UI no conecta con la API**: Comprobar que la API está en marcha y que `API_BASE_URL` apunta al host/puerto correctos. En Docker, si ves "unable to open database file", la API no arranca; la imagen incluye correcciones para permisos y ruta por defecto.
- **Docker “congelado” tras una barra de descarga ~461 MB**: Es normal con **Whisper local**. Primero se descarga el modelo; después la transcripción en **CPU** puede tardar **mucho más** que la duración del audio y no envía eventos hasta terminar. Revisa los logs (`Whisper local: transcribiendo…` / `transcripción terminada`). Para ir más rápido: `TRANSCRIPTION_BACKEND=cloud` y `OPENAI_API_KEY` (límite ~25 MB por archivo), o un modelo más pequeño (`TRANSCRIPTION_MODEL=tiny`).
- **ModuleNotFoundError**: Ejecutar `uv sync` de nuevo.
- **Puerto en uso**: Cambiar `--port` en uvicorn o la configuración de Gradio.

---

*Actualizado según implementación del Hello World E2E (US-000) y procesamiento de archivos TXT/MD (US-002).*
