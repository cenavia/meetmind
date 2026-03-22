# Implementation Plan: Ver extracción de participantes

**Branch**: `003-participants-extraction` | **Date**: 2025-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/003-participants-extraction/spec.md`

## Summary

Implementar el nodo `extract_participants` que extrae e identifica nombres de participantes a partir de `raw_text` usando un LLM con salida estructurada (Pydantic). El nodo se inserta entre `preprocess` y `mock_result`. Reglas: excluir términos genéricos y títulos; deduplicar; preferir variante más completa; orden por primera aparición; devolver "No identificados" cuando no hay nombres. El campo `participants` del State ya existe; `mock_result` deja de devolver `participants` para no sobrescribir la extracción real.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (sin persistencia para esta feature)  
**Testing**: pytest (tests unitarios para extract_participants, integración para flujo completo)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Extracción de participantes como parte del pipeline; tiempo total alineado con 001/002 (<30s para textos típicos)  
**Constraints**: Formato participants según spec; prompt debe instruir deduplicación, exclusión de genéricos/títulos, orden  
**Scale/Scope**: Un nodo adicional en el grafo; sin cambios en API ni UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Nodo en Core; API y UI sin cambios |
| II. Nodos autocontenidos | ✅ | extract_participants en `nodes/extract_participants/` con node.py y prompt.py |
| III. Formatos de salida | ✅ | participants: str, nombres por coma; "No identificados" cuando vacío (spec/clarify) |
| IV. Robustez ante información incompleta | ✅ | "No identificados" cuando no hay nombres; no inventar datos |
| V. Modularidad y testabilidad | ✅ | Nodo testeable aislado; prompts en módulo separado |
| VI. Agent Skills | ✅ | langgraph-fundamentals, langchain-fundamentals (structured output) |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/003-participants-extraction/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (participants field format)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   └── agents/
│       └── meeting/
│           ├── agent.py                          # MODIFICAR: añadir extract_participants, edge preprocess→extract_participants→mock_result
│           ├── state.py                          # Sin cambios (participants ya existe)
│           └── nodes/
│               ├── preprocess/
│               │   └── node.py                   # Sin cambios
│               ├── extract_participants/         # CREAR
│               │   ├── __init__.py
│               │   ├── node.py                   # Lógica: LLM + structured output, post-procesar (orden, dedup)
│               │   └── prompt.py                 # Prompt especializado
│               └── mock_result/
│                   └── node.py                   # MODIFICAR: no devolver participants (usa valor de state)
│
├── tests/
│   └── unit/
│       └── agents/
│           └── meeting/
│               └── nodes/
│                   └── extract_participants/
│                       └── test_extract_participants.py   # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión de la estructura 001/002. Nuevo nodo `extract_participants` autocontenido (Principio II). El grafo pasa de `preprocess → mock_result` a `preprocess → extract_participants → mock_result`. mock_result deja de incluir `participants` en su retorno para preservar el valor extraído por extract_participants.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
