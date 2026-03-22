# Implementation Plan: Ver acciones acordadas con responsables

**Branch**: `005-extract-actions` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/005-extract-actions/spec.md`

## Summary

Implementar el nodo `extract_actions` que extrae las acciones acordadas en la reunión con su responsable asignado usando un LLM con salida estructurada (Pydantic). Formato: "acción | responsable" por par; pares separados por punto y coma; orden por primera aparición; "Por asignar" cuando el responsable no es identificable; "No hay acciones identificadas" cuando 0 acciones. Reglas: variantes lingüísticas ("se encargará", "debe", "comprometió a"); consolidar redundantes prefiriendo variante más específica; varios responsables → primer mencionado; cargo sin nombre → "Por asignar"; reformular para evitar "|" y ";" en salida. El nodo se inserta entre `identify_topics` y `mock_result`. El campo `actions` del State ya existe; `mock_result` deja de devolver `actions`.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (sin persistencia para esta feature)  
**Testing**: pytest (tests unitarios para extract_actions, integración para flujo completo)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Extracción de acciones como parte del pipeline; tiempo total alineado con 001-004 (<30s para textos típicos)  
**Constraints**: Formato actions según spec (acción | responsable; pares separados por punto y coma; "No hay acciones identificadas" si vacío)  
**Scale/Scope**: Un nodo adicional en el grafo; mock_result deja de proporcionar actions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Nodo en Core; API sin cambios; UI hereda loader existente |
| II. Nodos autocontenidos | ✅ | extract_actions en `nodes/extract_actions/` con node.py y prompt.py |
| III. Formatos de salida | ✅ | actions: str, formato "acción \| responsable"; pares por punto y coma; "No hay acciones identificadas" cuando 0 |
| IV. Robustez ante información incompleta | ✅ | Sin responsable → "Por asignar"; sin acciones → "No hay acciones identificadas" |
| V. Modularidad y testabilidad | ✅ | Nodo testeable aislado; prompts en módulo separado |
| VI. Agent Skills | ✅ | langgraph-fundamentals, langchain-fundamentals (structured output) |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/005-extract-actions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (actions field format)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   └── agents/
│       └── meeting/
│           ├── agent.py                          # MODIFICAR: añadir extract_actions, edge identify_topics→extract_actions→mock_result
│           ├── state.py                          # Sin cambios (actions ya existe)
│           └── nodes/
│               ├── preprocess/
│               ├── extract_participants/
│               ├── identify_topics/
│               ├── extract_actions/              # CREAR
│               │   ├── __init__.py
│               │   ├── node.py                   # Lógica: LLM + structured output, post-procesar (orden, formato, sanitizar)
│               │   └── prompt.py                 # Prompt especializado
│               └── mock_result/
│                   └── node.py                   # MODIFICAR: no devolver actions (usa valor de state)
│
├── tests/
│   └── unit/
│       └── agents/
│           └── meeting/
│               └── nodes/
│                   └── extract_actions/
│                       └── test_extract_actions.py   # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión del grafo existente. Nuevo nodo `extract_actions` autocontenido (Principio II). El grafo pasa de `... → identify_topics → mock_result` a `... → identify_topics → extract_actions → mock_result`. mock_result deja de incluir `actions` en su retorno para preservar el valor extraído por extract_actions.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
