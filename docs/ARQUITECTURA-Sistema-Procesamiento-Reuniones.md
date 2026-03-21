# Documento de Arquitectura — MeetMind

> **Arquitectura del Sistema de Procesamiento de Reuniones con IA**  
> Proyecto: **MeetMind**  
> Fecha: 2025-03-21  
> Versión: 1.0  
> Estado: Definición de arquitectura (no implementación)  
> Referencia: [PRD-Sistema-Procesamiento-Reuniones-IA.md](./PRD-Sistema-Procesamiento-Reuniones-IA.md)

---

## Índice

- [1. Visión General](#1-visión-general)
- [2. Decisiones de Framework](#2-decisiones-de-framework)
- [3. Arquitectura por Capas](#3-arquitectura-por-capas)
- [4. Componentes del Sistema](#4-componentes-del-sistema)
- [5. Workflow LangGraph](#5-workflow-langgraph)
- [6. API REST (FastAPI)](#6-api-rest-fastapi)
- [7. Interfaz de Usuario (Gradio)](#7-interfaz-de-usuario-gradio)
- [8. Estructura de Directorios](#8-estructura-de-directorios)
- [9. Flujo de Datos](#9-flujo-de-datos)
- [10. Dependencias y Configuración](#10-dependencias-y-configuración)
- [11. Consideraciones de Diseño](#11-consideraciones-de-diseño)
- [12. Persistencia e Historial de Procesos](#12-persistencia-e-historial-de-procesos)

---

## 1. Visión General

### 1.1 Descripción

MeetMind es un sistema de **tres capas** que transforma grabaciones o notas de reuniones en documentación estructurada:

| Capa | Tecnología | Responsabilidad |
|------|------------|-----------------|
| **UI** | Gradio | Interfaz de usuario para carga de archivos y visualización de resultados |
| **API** | FastAPI | API REST para orquestar solicitudes y servir el workflow |
| **Core** | LangGraph + LangChain | Workflow de procesamiento con nodos especializados |

### 1.2 Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE PRESENTACIÓN                           │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  Gradio UI — File upload, Historial, Resultados (participantes,      ││
│  │  temas, acciones, minuta, resumen ejecutivo)                         ││
│  └─────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTP / Cliente Gradio
┌──────────────────────────────────▼──────────────────────────────────────┐
│                           CAPA DE API                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  FastAPI — Endpoints REST: POST /process, GET /meetings, etc.        ││
│  │  Validación (Pydantic), Manejo de errores, CORS, Persistencia        ││
│  └─────────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ Invocación del grafo
┌──────────────────────────────────▼──────────────────────────────────────┐
│                           CAPA DE NEGOCIO                                │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  LangGraph Workflow — 5 nodos + transcripción                        ││
│  │  extract_participants → identify_topics → extract_actions →          ││
│  │  generate_minutes → create_summary                                   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  LangChain — LLM, Prompts, Parsing estructurado                      ││
│  │  Servicio STT — Transcripción de audio/video (Whisper u otro)        ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Decisiones de Framework

### 2.1 Framework Selection (Skill: framework-selection)

Según el PRD y las skills del proyecto:

| Criterio | Decisión | Justificación |
|----------|----------|---------------|
| **Orquestación** | **LangGraph** | Workflow multi-nodo con control de flujo explícito, secuencia determinada y posible paralelización futura de extractores |
| **Modelos y prompts** | **LangChain** | Base para LLM, prompts y parsing estructurado (Pydantic) |
| **Deep Agents** | No | El flujo es acotado, no requiere planificación dinámica ni subagentes |
| **LangChain Agents** | No | No hay loop de herramientas; el flujo es un grafo lineal/secuencial |

### 2.2 Capa API y UI

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| **API REST** | FastAPI | Validación con Pydantic, async, documentación OpenAPI automática, convenciones modernas |
| **UI** | Gradio | Requisito PRD: "Interfaz de selección de archivos"; soporte nativo para File, Audio, Video; integración sencilla con backend Python |

---

## 3. Arquitectura por Capas

### 3.1 Capa de Presentación (Gradio)

- **Responsabilidad**: Capturar entrada (archivo multimedia o texto), invocar API y mostrar resultados.
- **Patrón**: La UI puede invocar la API REST (FastAPI) vía `httpx` o ejecutar el workflow directamente en el mismo proceso (modo demo).
- **Componentes**: `File` (upload), `Textbox` (notas), `Markdown`/`Textbox` (salidas).

### 3.2 Capa de API (FastAPI)

- **Responsabilidad**: Validar entradas, invocar el workflow LangGraph, devolver respuestas tipadas.
- **Patrón**: Routers por dominio; Dependencias para inyectar el grafo compilado.
- **Seguridad**: CORS, límites de tamaño de archivo, validación estricta.

### 3.3 Capa de Negocio (LangGraph + LangChain)

- **Responsabilidad**: Transcripción (si multimedia), extracción y generación mediante nodos especializados.
- **Patrón**: StateGraph con nodos que retornan actualizaciones parciales del estado.

---

## 4. Componentes del Sistema

### 4.1 Componentes Principales

| Componente | Ubicación lógica | Descripción |
|------------|------------------|-------------|
| **Transcriber** | `services/transcriber.py` | Convierte audio/video a texto (Whisper u otro STT) |
| **Workflow Graph** | `agents/meeting/agent.py` | Punto de entrada: construye y compila el grafo |
| **State Schema** | `agents/meeting/state.py` | Esquema TypedDict del estado compartido |
| **Nodos + Prompts** | `agents/meeting/nodes/<nodo>/` | Cada nodo: `node.py` + `prompt.py` en su carpeta |
| **Rutas** | `agents/meeting/routes/preprocess/` | Enrutamiento: multimedia vs texto |
| **API** | `api/main.py` | FastAPI + endpoints que consumen el agente |
| **Persistencia** | `db/`, `models/` | Modelos y acceso a BD para historial de reuniones |
| **Gradio App** | `ui/app.py` | Bloques, historial y event listeners |

### 4.2 Entradas y Salidas (alineadas con PRD)

| Entrada | Formatos | Destino |
|---------|----------|---------|
| Multimedia | MP4, MOV, MP3, WAV, M4A, WEBM, MKV | Transcriber → `raw_text` |
| Documentos | TXT, Markdown | Lectura directa → `raw_text` |

| Salida | Campo | Restricción |
|--------|-------|-------------|
| Participantes | `participants` | Nombres separados por comas |
| Temas | `topics` | 3-5 elementos, separados por punto y coma |
| Acciones | `actions` | Separadas por pipe (\|) |
| Minuta | `minutes` | Máx. 150 palabras |
| Resumen ejecutivo | `executive_summary` | Máx. 30 palabras |

---

## 5. Workflow LangGraph

### 5.1 Esquema de Estado (State Schema)

Alineado con Anexo A del PRD y LangGraph fundamentals:

```python
from typing_extensions import TypedDict
from typing import Optional

class MeetingState(TypedDict):
    """Estado compartido del workflow de procesamiento de reuniones."""
    raw_text: str                    # Texto fuente (transcripción o contenido)
    participants: str                # Nombres separados por comas
    topics: str                      # Temas separados por punto y coma
    actions: str                     # Acciones separadas por pipe
    minutes: str                     # Minuta formal (max 150 palabras)
    executive_summary: str           # Resumen (max 30 palabras)
    source_file: Optional[str]       # Nombre del archivo de origen
    processing_errors: list[str]     # Errores/advertencias durante el proceso
```

**Nota**: No se usan reducers (operator.add) en campos como `participants`, `topics`, etc., porque cada nodo sobrescribe su propio campo. Solo `processing_errors` podría usar reducer si se acumulan advertencias.

### 5.2 Grafo de Nodos

```
START
  │
  ▼
┌─────────────────────┐
│ preprocess / route  │  ← Opcional: detectar tipo de entrada, transcripción
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ extract_participants│  Nodo 1: extrae nombres
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ identify_topics     │  Nodo 2: identifica 3-5 temas
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ extract_actions     │  Nodo 3: extrae acciones y responsables
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ generate_minutes    │  Nodo 4: minuta formal (150 palabras)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ create_summary      │  Nodo 5: resumen ejecutivo (30 palabras)
└──────────┬──────────┘
           │
           ▼
          END
```

### 5.3 Posible Paralelización Futura

Según el PRD (sección 6.3): `extract_participants`, `identify_topics` y `extract_actions` son independientes entre sí. Opciones:

1. **Fase inicial**: flujo secuencial (simplicidad).
2. **Optimización posterior**: usar `Send` API de LangGraph para fan-out a los tres extractores y luego fan-in antes de `generate_minutes`, con reducer en los campos correspondientes.

### 5.4 Nodos — Responsabilidades

| Nodo | Input principal | Output | Herramientas LangChain |
|------|-----------------|--------|------------------------|
| `extract_participants` | `raw_text` | `participants` | LLM + prompt + `with_structured_output` o regex/parsing |
| `identify_topics` | `raw_text` | `topics` | LLM + prompt + validación 3-5 temas |
| `extract_actions` | `raw_text` | `actions` | LLM + prompt + parsing pipe |
| `generate_minutes` | `participants`, `topics`, `actions` | `minutes` | LLM + prompt (max 150 palabras) |
| `create_summary` | Toda la info | `executive_summary` | LLM + prompt (max 30 palabras) |

### 5.5 Checkpointer

- **Desarrollo**: `InMemorySaver` o sin checkpointer (flujo síncrono, sin multi-turno).
- **Producción (si aplica HITL o reanudación)**: `PostgresSaver` o `SqliteSaver`.
- Para el caso base de procesamiento "fire-and-forget", el checkpointer puede omitirse.

---

## 6. API REST (FastAPI)

### 6.1 Endpoints Propuestos

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/process/file` | Procesar archivo (multipart: audio/video/texto) |
| `POST` | `/api/v1/process/text` | Procesar texto plano (JSON body) |
| `GET` | `/api/v1/meetings` | Listar historial de reuniones procesadas |
| `GET` | `/api/v1/meetings/{id}` | Detalle de una reunión procesada |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/jobs/{job_id}` | (Opcional) Estado de job async si se implementa cola |

### 6.2 Modelos Pydantic (Request/Response)

**Request — procesar texto**:
```python
class ProcessTextRequest(BaseModel):
    text: str
    source_name: str | None = None
```

**Request — procesar archivo**: `UploadFile` (FastAPI) con validación de tipos MIME.

**Response**:
```python
class ProcessMeetingResponse(BaseModel):
    id: str                           # ID del registro persistido
    participants: str
    topics: str
    actions: str
    minutes: str
    executive_summary: str
    source_file: str | None = None
    processing_errors: list[str] = []
    created_at: datetime              # Fecha de procesamiento
```

### 6.3 Estructura de Routers

- `routers/process.py`: endpoints de procesamiento (POST /process/*).
- `routers/meetings.py`: endpoints de historial (GET /meetings, GET /meetings/{id}).
- `routers/health.py`: health check.
- Uso de `Annotated` y `Depends` para inyección del grafo compilado y sesión de BD.

### 6.4 Async vs Sync

- Endpoints que invocan el grafo: usar `def` (no `async def`) si el grafo se ejecuta de forma síncrona, para no bloquear el event loop; o ejecutar en `run_in_executor` si se prefiere mantener la API async.

---

## 7. Interfaz de Usuario (Gradio)

### 7.1 Componentes

| Componente | Uso |
|------------|-----|
| `gr.File` | Upload de archivos (audio, video, TXT, MD) con `file_types` adecuados |
| `gr.Textbox` | Entrada de texto/notas alternativo |
| `gr.Button` | "Procesar reunión" |
| `gr.Markdown` / `gr.Textbox` | Salidas: participantes, temas, acciones, minuta, resumen |
| `gr.Dataframe` / `gr.Dropdown` | Historial: lista de reuniones procesadas |
| `gr.Progress` | Indicador de progreso durante el procesamiento |

### 7.2 Patrón de Integración

**Opción A — Gradio llama a la API**:
- Gradio corre en proceso separado o en el mismo.
- `fn` del botón hace `httpx.post("http://api/process", ...)` y muestra la respuesta.

**Opción B — Gradio usa el grafo directamente**:
- Gradio y FastAPI comparten el módulo del grafo.
- La `fn` invoca `graph.invoke(...)` directamente (útil para demos y desarrollo).

### 7.3 Event Listeners

- `btn.click(fn=process_meeting, inputs=[file_input, text_input], outputs=[participants_out, topics_out, ...])`
- `show_progress="full"` para feedback visual.
- Considerar `queue=True` para evitar timeouts en procesos largos.

---

## 8. Estructura de Directorios

Estructura escalable siguiendo el patrón **un agente por carpeta**, con nodos autocontenidos (node + prompt + tools por carpeta) y rutas de enrutamiento separadas. Permite añadir nuevos agentes (ej. `summarizer`, `translation`) sin tocar el existente.

### 8.1 Árbol de Directorios

```
meetmind/
├── src/
│   ├── api/
│   │   ├── main.py                 ← FastAPI app + montaje de routers
│   │   ├── dependencies.py         ← Depends: grafo, transcriber, get_session
│   │   └── routers/
│   │       ├── process.py          ← POST /process/file, POST /process/text
│   │       ├── meetings.py         ← GET /meetings, GET /meetings/{id}
│   │       └── health.py           ← GET /health
│   │
│   ├── db/
│   │   ├── models.py               ← Modelo MeetingRecord (SQLModel/SQLAlchemy)
│   │   ├── session.py              ← Session factory, engine
│   │   └── repositories/
│   │       └── meetings.py         ← CRUD de reuniones procesadas
│   │
│   ├── agents/
│   │   └── meeting/
│   │       ├── agent.py            ← Punto de entrada: construye y compila el grafo
│   │       ├── state.py            ← Definición de MeetingState (TypedDict)
│   │       │
│   │       ├── nodes/
│   │       │   ├── extract_participants/
│   │       │   │   ├── node.py     ← Lógica del nodo
│   │       │   │   └── prompt.py   ← Prompt del extractor de participantes
│   │       │   │
│   │       │   ├── identify_topics/
│   │       │   │   ├── node.py     ← Lógica del nodo
│   │       │   │   └── prompt.py   ← Prompt del analizador de temas
│   │       │   │
│   │       │   ├── extract_actions/
│   │       │   │   ├── node.py     ← Lógica del nodo
│   │       │   │   └── prompt.py   ← Prompt del extractor de acciones
│   │       │   │
│   │       │   ├── generate_minutes/
│   │       │   │   ├── node.py     ← Lógica del nodo
│   │       │   │   └── prompt.py   ← Prompt del generador de minutas
│   │       │   │
│   │       │   └── create_summary/
│   │       │       ├── node.py     ← Lógica del nodo
│   │       │       └── prompt.py   ← Prompt del creador de resumen
│   │       │
│   │       └── routes/
│   │           └── preprocess/
│   │               ├── route.py    ← Función de enrutamiento: multimedia vs texto
│   │               └── prompt.py   ← (Opcional) Prompt si el router usa LLM
│   │
│   ├── services/
│   │   ├── transcriber.py          ← STT (Whisper, API cloud, etc.)
│   │   └── file_loader.py          ← Carga de archivos TXT/MD
│   │
│   ├── ui/
│   │   └── app.py                  ← Gradio Blocks app
│   │
│   └── config.py                   ← Configuración (env, modelos, paths)
│
├── tests/
│   ├── unit/
│   │   ├── agents/
│   │   │   └── meeting/
│   │   │       ├── test_nodes.py
│   │   │       └── test_state.py
│   │   └── db/
│   │       └── test_meetings_repository.py
│   └── integration/
│       └── test_api.py
│
├── docs/
│   ├── PRD-Sistema-Procesamiento-Reuniones-IA.md
│   └── ARQUITECTURA-Sistema-Procesamiento-Reuniones.md
│
├── pyproject.toml
├── requirements.txt
└── .env.example
```

### 8.2 Ventajas de esta Estructura

| Aspecto | Beneficio |
|---------|-----------|
| **Un nodo = una carpeta** | Cada nodo agrupa `node.py`, `prompt.py` y (si aplica) `tools.py`; cambios localizados. |
| **Un agente = una carpeta** | `agents/meeting/` es autocontenido; futuros agentes (`agents/summarizer/`, etc.) no afectan al existente. |
| **Rutas separadas** | `routes/preprocess/` centraliza la lógica de decisión (transcribir vs texto directo) y su prompt si usa LLM. |
| **API desacoplada** | `api/` solo consume el agente compilado vía `dependencies.py`; no conoce la estructura interna del grafo. |
| **Tests alineados** | `tests/unit/agents/meeting/` refleja la estructura de código. |

### 8.3 Crecimiento Futuro

Ejemplo de cómo escalar añadiendo un agente de resumen de múltiples reuniones:

```
src/agents/
├── meeting/           ← Agente actual (una reunión)
│   ├── agent.py
│   ├── state.py
│   ├── nodes/
│   └── routes/
│
└── batch_summary/     ← Nuevo agente (múltiples reuniones)
    ├── agent.py
    ├── state.py
    ├── nodes/
    │   ├── aggregate/
    │   └── synthesize/
    └── routes/
```

Cada agente mantiene su propio `state.py`, `nodes/` y `routes/` sin interferir con los demás.

---

## 9. Flujo de Datos

### 9.1 Procesamiento de Archivo Multimedia

```
Usuario sube MP4/MP3/etc.
    → API recibe UploadFile
    → Transcriber transcribe a texto
    → State inicial: { raw_text: "...", source_file: "reunion.mp4" }
    → graph.invoke(initial_state)
    → Persistir resultado en BD (MeetingRecord)
    → Response con id, participants, topics, actions, minutes, executive_summary, created_at
```

### 9.2 Procesamiento de Texto/Documento

```
Usuario sube TXT/MD o pega texto
    → file_loader lee contenido O API recibe JSON con text
    → State inicial: { raw_text: "...", source_file: "notas.md" }
    → graph.invoke(initial_state)
    → Persistir resultado en BD (MeetingRecord)
    → Response con todas las salidas + id + created_at
```

### 9.3 Consulta de Historial

```
Usuario solicita historial (GET /meetings) o detalle (GET /meetings/{id})
    → API consulta repositorio
    → BD devuelve MeetingRecord(s)
    → Response con lista o detalle de reuniones procesadas
```

### 9.4 Manejo de Errores

| Escenario | Estrategia |
|-----------|------------|
| Transcripción fallida | `processing_errors.append("...")`, retornar estado parcial o error HTTP 422 |
| LLM falla en un nodo | RetryPolicy (transitorio) o capturar y añadir a `processing_errors` |
| Texto vacío o muy corto | Validación en API; en nodos, retornar valores por defecto o mensaje "[Información limitada]" |
| Archivo no soportado | Validación MIME en API, respuesta 400 |

---

## 10. Dependencias y Configuración

### 10.1 Paquetes Principales (Python)

Según langchain-dependencies y requisitos del PRD:

| Paquete | Versión | Uso |
|---------|---------|-----|
| `langchain` | >=1.0,<2.0 | Base |
| `langchain-core` | >=1.0,<2.0 | Tipos e interfaces |
| `langgraph` | >=1.0,<2.0 | StateGraph, nodos, compilación |
| `langsmith` | >=0.3.0 | Trazabilidad (opcional) |
| `langchain-openai` o `langchain-anthropic` | latest | Modelo LLM |
| `fastapi` | latest | API REST |
| `uvicorn` | latest | Servidor ASGI |
| `gradio` | latest | UI |
| `httpx` | latest | Cliente HTTP (si Gradio llama API) |
| `pydantic` | >=2 | Validación |
| `sqlmodel` | latest | ORM (modelos + migraciones; preferible sobre SQLAlchemy puro) |
| `aiosqlite` o `asyncpg` | latest | Driver async para SQLite/PostgreSQL |

### 10.2 Transcripción (STT)

- **Opciones**: OpenAI Whisper API, `openai-whisper` (local), o servicio cloud (Google, AWS).
- Definir en `config.py` el proveedor y las claves de entorno.

### 10.3 Variables de Entorno

```bash
# LLM
OPENAI_API_KEY=...
# o ANTHROPIC_API_KEY=...

# Transcripción (si aplica)
WHISPER_API_KEY=...  # o equivalente

# Base de datos (persistencia de historial)
DATABASE_URL=sqlite+aiosqlite:///./meetmind.db
# Producción: postgresql+asyncpg://user:pass@host/db

# LangSmith (opcional)
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=meetmind
```

---

## 11. Consideraciones de Diseño

### 11.1 Modularidad

- Cada nodo en un archivo separado para facilitar tests unitarios.
- Prompts en módulo dedicado para ajustes sin tocar lógica.

### 11.2 Robustez (PRD 12.4)

- Sin participantes: `"No identificados"` o lista vacía.
- Menos de 3 temas: retornar los disponibles.
- Acciones implícitas: responsable `"Por asignar"`.
- Texto muy corto: prefijo `[Información limitada]` en salidas.

### 11.3 Escalabilidad Futura

- Cola de jobs (Celery, RQ, etc.) si el procesamiento se hace async.
- Endpoint `GET /jobs/{id}` para consultar estado.
- Checkpointer con PostgresSaver si se requiere reanudación o HITL.
- Búsqueda semántica en historial (excluida en v1 del PRD) usando embeddings + vector store.

### 11.4 Seguridad

- Validar tipos MIME y extensiones en uploads.
- Límite de tamaño de archivo configurable.
- No exponer rutas internas ni secrets en logs.

---

## 12. Persistencia e Historial de Procesos

La plataforma **persiste el historial** de todas las transcripciones y procesamientos realizados. Cada reunión procesada se guarda en base de datos para permitir consultas posteriores.

### 12.1 Modelo de Datos

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class MeetingRecord(SQLModel, table=True):
    """Registro persistido de una reunión procesada."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    source_file: Optional[str] = None
    raw_text: str = ""                    # Transcripción o contenido original
    participants: str = ""
    topics: str = ""
    actions: str = ""
    minutes: str = ""
    executive_summary: str = ""
    processing_errors: str = "[]"         # JSON array de errores
    status: str = "completed"             # completed | failed | partial
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 12.2 Flujo de Persistencia

| Paso | Acción |
|------|--------|
| 1 | Tras `graph.invoke()`, el resultado está en `MeetingState` |
| 2 | El endpoint de proceso crea un `MeetingRecord` a partir del estado |
| 3 | El repositorio persiste en BD (`create()` o `insert()`) |
| 4 | Se retorna al cliente el `id` y los datos (incluido `created_at`) |

### 12.3 Repositorio y Sesión

- **Ubicación**: `db/repositories/meetings.py`
- **Operaciones**: `create(record)`, `get_by_id(id)`, `list(limit, offset, order_by)`
- **Sesión**: `db/session.py` expone `get_session()` para inyección vía `Depends(get_session)` en los endpoints

### 12.4 Diferencia con el Checkpointer de LangGraph

| Concepto | Propósito | Alcance |
|----------|-----------|---------|
| **Checkpointer (LangGraph)** | Guardar estado de ejecución del grafo para reanudar o HITL | Por thread_id, por invocación |
| **MeetingRecord (BD)** | Historial de reuniones procesadas para consulta del usuario | Permanente, todas las reuniones |

El checkpointer es opcional y sirve para la ejecución del workflow. La persistencia en BD es **obligatoria** para el historial de la plataforma.

### 12.5 UI de Historial

- **Lista**: `gr.Dataframe` o `gr.Dropdown` con reuniones recientes (id, source_file, created_at, executive_summary).
- **Selección**: Al elegir una reunión, cargar detalle vía `GET /meetings/{id}` y mostrar participantes, temas, acciones, minuta y resumen en los componentes de salida.

---

*Documento de arquitectura MeetMind. Base para implementación por fases según PRD.*
