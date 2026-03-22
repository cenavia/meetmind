# Implementation Plan: Procesar notas en texto

**Branch**: `002-text-notes-processing` | **Date**: 2025-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/002-text-notes-processing/spec.md`

## Summary

Extender el flujo existente de MeetMind para aceptar archivos TXT y Markdown además de texto directo. El usuario puede elegir entre pegar texto o subir archivo en la misma pantalla; el contenido se lee sin transcripción y pasa al workflow de extracción. Nuevos componentes: `file_loader` (servicio), endpoint `/process/file`, y UI con `gr.File` + bloqueo mutuo entre texto/archivo. El preprocess no requiere cambios; la API extrae el contenido y pasa `raw_text` al grafo. Validaciones: extensión/MIME, encoding (UTF-8, fallback latin-1), límite 50k caracteres, archivo vacío.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (no persistencia de archivos; se procesan en memoria)  
**Testing**: pytest (tests unitarios para file_loader, integración para endpoint file)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Subida + procesamiento <30s para archivos típicos (hasta 5.000 caracteres)  
**Constraints**: Límite 50.000 caracteres; formatos solo .txt y .md; validación MIME (Constitución)  
**Scale/Scope**: Extensión del flujo único existente; sin concurrencia especial

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | API valida y delega; Core procesa; UI solo captura y muestra. File loader en services (capa de soporte) |
| II. Nodos autocontenidos | ✅ | preprocess existente se extiende; no se crean nodos nuevos; file_loader es servicio, no nodo |
| III. Formatos de salida | ✅ | Misma respuesta que /process/text; participants, topics, actions, minutes, executive_summary |
| IV. Robustez ante información incompleta | ✅ | Validación extensión, MIME, vacío, límite; mensajes claros en rechazos |
| V. Modularidad y testabilidad | ✅ | file_loader testeable aislado; endpoint con Depends; preprocess sin cambios de firma |
| VI. Agent Skills | ✅ | fastapi (UploadFile, File()), gradio (gr.File, gr.UploadButton), langgraph-fundamentals |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/002-text-notes-processing/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contract file upload)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── api/
│   │   └── routers/
│   │       └── process.py       # AÑADIR: endpoint POST /process/file (UploadFile)
│   │
│   ├── agents/
│   │   └── meeting/
│   │       └── nodes/
│   │           └── preprocess/
│   │               └── node.py  # Sin cambios (API inyecta raw_text)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── file_loader.py       # CREAR: load_text_file(path|bytes, ext) → str
│   │
│   └── ui/
│       └── app.py               # MODIFICAR: gr.File, bloqueo mutuo, barra progreso, "Procesando..."
│
├── tests/
│   ├── unit/
│   │   └── services/
│   │       └── test_file_loader.py   # CREAR
│   └── integration/
│       └── test_api_process_file.py  # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión de la estructura 001. Se crea `src/services/` para `file_loader` (capa de soporte entre API y Core). El preprocess no necesita detectar "archivo vs texto" porque la API ya extrae el contenido y pasa `raw_text` al grafo; la detección ocurre en la API al recibir multipart vs JSON.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
