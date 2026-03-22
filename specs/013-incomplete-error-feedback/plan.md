# Implementation Plan: Feedback ante información incompleta y errores (US-011 / spec 013)

**Branch**: `013-incomplete-error-feedback` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/013-incomplete-error-feedback/spec.md`

## Summary

Unificar el **feedback humano** en las tres capas (LangGraph, FastAPI, Gradio) según la spec y las aclaraciones: estados `completed` / `partial` / `failed`, **advertencias estructuradas** (`processing_errors` como lista coherente en estado, API y persistencia), **mensajes en español** sin trazas en cuerpos públicos, validación de **texto corto** (umbral por defecto **20 palabras**, recuento por espacios en `raw_text` tras strip), **interfaz** con bloque de avisos separado del análisis (scroll para listas largas), **etiquetas de estado en texto**, acordeón **Detalles técnicos** (colapsado, sin secretos), y **transcripción copiable** cuando el flujo exponga `transcript` / texto transcrito. La **API REST** debe devolver el mismo modelo semántico que consume la UI (FR-013, FR-015).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, LangGraph/LangChain, Gradio, SQLModel/SQLAlchemy 2.x, httpx (UI → API)  
**Storage**: SQLite por defecto (`MeetingRecord.processing_errors` como `Text`; serialización acordada en [data-model.md](./data-model.md))  
**Testing**: pytest — `tests/unit/` (nodos, `meeting_persist`, helpers de mensajes); `tests/integration/api/` (cuerpos JSON sin fugas, listas de errores); pruebas manuales/UI según [quickstart.md](./quickstart.md)  
**Target Platform**: Servidor ASGI + app Gradio  
**Project Type**: Web app (API + UI en monorepo `src/`)  
**Performance Goals**: Sin objetivo nuevo; mantener timeouts existentes (`get_processing_timeout_sec`)  
**Constraints**: CORS/config actuales; no exponer secretos en “detalles técnicos”; mensajes de error HTTP ya orientados a persona deben permanecer o mejorarse en español  
**Scale/Scope**: Una app; historial en UI/API cuando exista (FR-012) reutiliza el mismo patrón de presentación

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Reglas de negocio (umbral palabras, acumulación de errores) en nodos/API; UI solo mapea campos y validación local de vacío/archivo |
| II. Nodos autocontenidos | ✅ | Cambios preferentes en `preprocess` y nodos que añaden advertencias; prompts en `prompt.py` si se añaden mensajes generados por LLM |
| III. Formatos de salida estructurados | ✅ | PRD en salidas analíticas; nuevos campos son metadatos (`status`, lista de avisos, `transcript` opcional) |
| IV. Robustez ante información incompleta | ✅ | Alineado con spec 013 + constitution: participantes, texto corto, transcripción fallida; unificar con lista `processing_errors` y `status` explícito en respuestas |
| V. Modularidad y testabilidad | ✅ | Helpers para mapear excepciones → mensaje español; tests por capa |
| VI. Agent Skills | ✅ | Implementación: `langgraph-fundamentals`, `fastapi`, `gradio` |

**Gates**: PASS. Sin filas obligatorias en Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/013-incomplete-error-feedback/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── processing-feedback.md
└── tasks.md              # /speckit.tasks (no creado por este comando)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── agents/meeting/
│   │   ├── state.py                 # MODIFICAR: processing_errors como lista + reducer LangGraph si aplica
│   │   ├── nodes/preprocess/       # MODIFICAR: recuento palabras, advertencia texto corto
│   │   ├── nodes/*/node.py         # REVISAR: acumular avisos con append, try/except → mensajes amigables
│   │   └── agent.py                # REVISAR: configuración de estado reducido si se usa Annotated reducer
│   ├── api/
│   │   ├── main.py                 # MODIFICAR: handlers globales → detail español, sin stack
│   │   ├── routers/process.py      # MODIFICAR: ProcessMeetingResponse extendido; mapeo dict→DTO
│   │   ├── routers/meetings.py     # MODIFICAR: lista en processing_errors o campo paralelo (ver data-model)
│   │   └── process_file_stream.py  # MODIFICAR: eventos finales coherentes con nuevo shape
│   ├── db/
│   │   ├── meeting_persist.py      # MODIFICAR: status failed vs partial; serialización errores
│   │   ├── models.py               # OPCIONAL: migración si se cambia tipo columna
│   │   └── repository.py           # REVISAR si cambia firma
│   ├── services/transcription.py   # MODIFICAR: errores → mensajes español + códigos internos solo en logs
│   └── ui/
│       ├── app.py                  # MODIFICAR: bloque avisos, estado textual, transcripción+copy, acordeón técnico, tema/layout
│       ├── status_loader.py        # MODIFICAR/AJUSTAR: tokens CSS tema
│       └── theme.py                # CREAR (opcional): factoría gr.themes MeetMind
├── tests/unit/ ...
└── tests/integration/api/ ...
```

**Structure Decision**: Monorepo existente; cambios transversales coordinados estado → API → persistencia → UI.

## Complexity Tracking

> Sin violaciones de constitución. Ninguna fila obligatoria.

## Phase 0 & 1 outputs

| Artefacto | Ruta |
|-----------|------|
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| Contracts | [contracts/processing-feedback.md](./contracts/processing-feedback.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

### Post Phase 1 — Constitution re-check

Los contratos mantienen la API como fachada; el grafo no se expone directamente. La UI sigue sin lógica de negocio de extracción. **Gates**: PASS.
