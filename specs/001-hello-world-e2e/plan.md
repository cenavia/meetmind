# Implementation Plan: Estructura inicial y Hello World E2E

**Branch**: `001-hello-world-e2e` | **Date**: 2025-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-hello-world-e2e/spec.md`

## Summary

Establecer el esqueleto del proyecto MeetMind con tres capas (API FastAPI, Core LangGraph, UI Gradio) y un flujo end-to-end mínimo donde: (1) el usuario introduce texto en Gradio, (2) la UI invoca la API por HTTP, (3) la API ejecuta un grafo LangGraph que retorna datos mock, (4) la UI muestra el resultado. Todo ejecutable según `COMO-EJECUTAR.md`. Validaciones: texto vacío en UI, límite 50k caracteres en API, estado de carga en UI, `API_BASE_URL` configurable.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv (gestor)  
**Storage**: N/A en Hello World (no persistencia)  
**Testing**: pytest (estructura base; tests mínimos opcionales)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Health <2s, procesamiento mock <5s (SC-002, SC-003)  
**Constraints**: Límite texto 50.000 caracteres; API_BASE_URL por entorno  
**Scale/Scope**: Flujo único, sin concurrencia; validación de setup

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | API FastAPI, Core LangGraph, UI Gradio; UI llama a API (no al grafo) |
| II. Nodos autocontenidos | ⚠️ Simplificado | Hello World: grafo mínimo con `preprocess` + nodo mock; estructura `nodes/` preparada para expansión futura |
| III. Formatos de salida | ✅ | participants, topics, actions, minutes, executive_summary según PRD/Constitución |
| IV. Robustez ante información incompleta | ⚠️ Parcial | Validación texto vacío en UI; límite longitud en API; resto en fases posteriores |
| V. Modularidad y testabilidad | ✅ | Grafo inyectable vía Depends; estructura de tests alineada |
| VI. Agent Skills | ✅ | framework-selection, langgraph-fundamentals, langchain-dependencies, fastapi, gradio |

**Gates**: PASS. Simplificaciones justificadas en Complexity Tracking (fase Hello World).

## Project Structure

### Documentation (this feature)

```text
specs/001-hello-world-e2e/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contract)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, /health, montaje routers
│   │   ├── dependencies.py      # Depends: get_graph
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py        # GET /health
│   │       └── process.py       # POST /api/v1/process/text
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── meeting/
│   │       ├── __init__.py
│   │       ├── agent.py         # get_graph(), StateGraph mínimo
│   │       ├── state.py         # MeetingState TypedDict
│   │       └── nodes/
│   │           ├── __init__.py
│   │           ├── preprocess/
│   │           │   ├── __init__.py
│   │           │   └── node.py  # Normaliza raw_text
│   │           └── mock_result/
│   │               ├── __init__.py
│   │               └── node.py  # Retorna datos hardcodeados
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   └── app.py               # Gradio: input, botón, output, httpx → API
│   │
│   └── config.py                # Settings (API_BASE_URL, etc.)
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   └── agents/
│   │       └── meeting/
│   │           └── test_agent.py   # (opcional para Hello World)
│   └── integration/
│       └── test_api_health.py      # (opcional)
│
├── docs/
│   └── planning/
│       └── COMO-EJECUTAR.md
│
├── pyproject.toml
├── .env.example
└── README.md
```

**Structure Decision**: Estructura única (monolito) con `src/` siguiendo ARQUITECTURA 8.1. En esta fase no se crean `db/`, `services/`, ni los 5 nodos completos; solo preprocess + mock_result para validar el flujo. La estructura permite añadir nodos reales en US posteriores.

## Complexity Tracking

| Simplificación | Justificación | Alternativa rechazada |
|----------------|---------------|------------------------|
| Un solo nodo de resultado (mock) en vez de 5 nodos reales | Hello World valida integración, no lógica de extracción; evita dependencia LLM en setup | 5 nodos con LLM real: bloquea validación sin API key y añade complejidad innecesaria |
| Sin capa `db/` ni persistencia | US-000 no requiere historial; SC-005 exige flujo reproducible sin BD | Añadir MeetingRecord: fuera de alcance de esta US |
| Nodos `preprocess` + `mock_result` sin carpetas completas (node+prompt) | mock_result no usa prompt; preprocess puede ser trivial | Estructura completa por nodo: overkill para datos hardcodeados |
| Gradio sin `gr.File` | Solo entrada de texto en Hello World | File upload: US posterior (procesamiento multimedia) |
