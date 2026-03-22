# MeetMind

## a. Descripción general del proyecto

MeetMind es un sistema que **procesa notas y grabaciones de reuniones** y devuelve un resultado estructurado con ayuda de un grafo de agentes (LangGraph): participantes, temas, acciones, minuta y resumen ejecutivo. Incluye una **API REST** (FastAPI) que orquesta el flujo, **persistencia** de reuniones en base de datos (SQLite por defecto), **transcripción** de audio y vídeo (Whisper vía OpenAI o modelo local) y una **interfaz web** (Gradio) que consume la API. El diseño contempla estados de proceso, avisos y errores parciales para dar **feedback claro** cuando el análisis es incompleto o falla una parte del pipeline.

## b. Stack tecnológico utilizado

| Área | Tecnologías |
|------|-------------|
| Lenguaje y runtime | Python 3.11+ |
| Gestión de dependencias y entorno | [uv](https://docs.astral.sh/uv/) |
| API | FastAPI, Uvicorn, Pydantic v2 |
| UI | Gradio |
| Agentes y orquestación | LangGraph, LangChain (langchain-core, langchain-openai) |
| Persistencia | SQLModel, SQLAlchemy 2.x; SQLite por defecto (`DATABASE_URL`) o URL compatible con SQLAlchemy |
| Cliente HTTP (UI → API) | httpx |
| IA / voz | OpenAI API (incl. `whisper-1`), paquete `openai-whisper` (local), `imageio-ffmpeg` / ffmpeg en sistema para multimedia |
| Configuración | python-dotenv |
| Pruebas (opcional) | pytest (`uv sync --extra dev` o dependencias de desarrollo según `pyproject.toml`) |

## c. Instalación y ejecución

### Requisitos previos

- Python 3.11 o superior
- [uv](https://docs.astral.sh/uv/) instalado
- Para multimedia: ffmpeg disponible en el PATH (recomendado; la API lo detecta al arrancar)
- Opcional: `OPENAI_API_KEY` para modelos cloud y transcripción por API

### Instalación

```bash
cd meetmind
uv sync
cp .env.example .env   # ajustar variables según necesidad
```

### Ejecutar la API

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

- Base: http://localhost:8000  
- OpenAPI interactiva: http://localhost:8000/docs  
- Salud: `GET /health` (liveness), `GET /ready` (readiness)

### Ejecutar la UI (Gradio)

En otra terminal:

```bash
uv run gradio src/ui/app.py
```

Si la API no está en `http://localhost:8000`:

```bash
API_BASE_URL=http://localhost:8000 uv run gradio src/ui/app.py
```

La UI suele abrirse en http://localhost:7860.

### Pruebas

Desde la raíz del repositorio:

```bash
uv run pytest
```

### Documentación ampliada

Instrucciones detalladas, ejemplos con `curl` y tabla de variables de entorno: [docs/planning/COMO-EJECUTAR.md](docs/planning/COMO-EJECUTAR.md).

## d. Estructura del proyecto

```text
meetmind/
├── src/                      # Código de aplicación (paquete instalable)
│   ├── api/                  # FastAPI: main, routers (health, process, meetings), streaming SSE
│   ├── agents/meeting/       # Grafo LangGraph, nodos (preproceso, participantes, temas, acciones, minuta, resumen)
│   ├── db/                   # Modelos SQLModel, repositorio, persistencia y codecs de errores
│   ├── services/             # Carga de archivos, transcripción, utilidades ffmpeg
│   ├── ui/                   # Aplicación Gradio, tema, layout de resultados, cliente SSE
│   └── config.py             # Variables de entorno y valores por defecto
├── tests/                    # Pruebas unitarias e integración (API, agentes, BD)
├── docs/                     # Documentación de planificación y guías
├── specs/                    # Especificaciones por feature (contratos, modelo de datos, planes)
├── pyproject.toml            # Metadatos del proyecto y dependencias
├── .env.example              # Plantilla de configuración
└── README.md
```


## e. Funcionalidades principales

- **Procesamiento desde texto**: envío de notas de reunión; el grafo extrae participantes, temas, acciones, genera minuta y resumen ejecutivo.
- **Procesamiento desde archivo**: soporte para `.txt` / `.md` y archivos multimedia (p. ej. MP4, MOV, MP3, WAV, M4A, WEBM, MKV) con transcripción previa cuando aplica.
- **API REST v1**: `POST /api/v1/process/text`, `POST /api/v1/process/file`; variantes **streaming** con Server-Sent Events (`/process/text/stream`, `/process/file/stream`) para fases de progreso.
- **Respuesta enriquecida**: `status`, lista `processing_errors`, `transcript` cuando hubo STT, y `meeting_id` si la persistencia tuvo éxito.
- **Historial**: `GET /api/v1/meetings` y detalle por id para consultar reuniones guardadas.
- **Salud del servicio**: endpoints de liveness y readiness para despliegues y monitorización.
- **Interfaz Gradio**: carga de texto o archivo, procesamiento contra la API, visualización del resultado y mensajes de estado/avisos acordes al contrato de feedback.

## f. Flujo de trabajo (metodología)

El proyecto sigue **desarrollo guiado por especificaciones (SDD)**: cada entrega relevante se documenta antes en `specs/<número>-<feature>/` (especificación, plan de implementación, investigación, modelo de datos, contratos API/UI, `tasks.md` y checklists), alineada con la constitución del producto en `.specify/memory/constitution.md` y ramas por feature; a partir de ahí se implementa y prueba en `src/` y `tests/`. La herramienta que permitió estructurar este flujo es **[GitHub Spec Kit](https://github.com/github/spec-kit)** (Specify / Speckit en el repositorio: plantillas, scripts y paso spec → plan → tareas bajo `.specify/`), y el contexto técnico activo se refleja en reglas del IDE (p. ej. `.cursor/rules/specify-rules.mdc`); las historias de usuario de planificación viven además en `docs/planning/`.

