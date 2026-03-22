# Implementation Plan: Ver temas principales discutidos

**Branch**: `004-identify-topics` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/004-identify-topics/spec.md`

## Summary

Implementar el nodo `identify_topics` que extrae entre 3 y 5 temas principales del texto de reunión usando un LLM con salida estructurada (Pydantic). El nodo se inserta entre `extract_participants` y `mock_result`. Reglas: granularidad apropiada (evitar genéricos); consolidar temas solapados preferiendo la variante más específica; orden por primera aparición; separador punto y coma; "No hay temas identificados" cuando 0 temas. El campo `topics` del State ya existe; `mock_result` deja de devolver `topics`. Además, la UI debe mostrar loader visible durante el procesamiento (Gradio `show_progress`) y ocultarlo mostrando mensaje de error cuando falla (ya cubierto por el flujo actual).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (sin persistencia para esta feature)  
**Testing**: pytest (tests unitarios para identify_topics, integración para flujo completo)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Extracción de temas como parte del pipeline; tiempo total alineado con 001/002/003 (<30s para textos típicos)  
**Constraints**: Formato topics según spec (3-5 elementos, punto y coma, orden primera aparición, "No hay temas identificados" si vacío)  
**Scale/Scope**: Un nodo adicional en el grafo; modificación menor en UI (verificar loader) y mock_result

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Nodo en Core; API sin cambios; UI solo verificar loader |
| II. Nodos autocontenidos | ✅ | identify_topics en `nodes/identify_topics/` con node.py y prompt.py |
| III. Formatos de salida | ✅ | topics: str, 3-5 elementos separados por punto y coma; "No hay temas identificados" cuando 0 |
| IV. Robustez ante información incompleta | ✅ | Menos de 3 temas: retornar disponibles sin forzar; 0 temas: "No hay temas identificados" |
| V. Modularidad y testabilidad | ✅ | Nodo testeable aislado; prompts en módulo separado |
| VI. Agent Skills | ✅ | langgraph-fundamentals, langchain-fundamentals (structured output), gradio (loader) |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/004-identify-topics/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (topics field format)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   └── agents/
│       └── meeting/
│           ├── agent.py                          # MODIFICAR: añadir identify_topics, edge extract_participants→identify_topics→mock_result
│           ├── state.py                          # Sin cambios (topics ya existe)
│           └── nodes/
│               ├── preprocess/
│               │   └── node.py                   # Sin cambios
│               ├── extract_participants/
│               │   └── ...                       # Sin cambios
│               ├── identify_topics/              # CREAR
│               │   ├── __init__.py
│               │   ├── node.py                   # Lógica: LLM + structured output, post-procesar (orden, consolidar, formato)
│               │   └── prompt.py                 # Prompt especializado
│               └── mock_result/
│                   └── node.py                   # MODIFICAR: no devolver topics (usa valor de state)
│
├── src/
│   └── ui/
│       └── app.py                                # VERIFICAR: loader durante procesamiento (show_progress=True); errores ya muestran mensaje
│
├── tests/
│   └── unit/
│       └── agents/
│           └── meeting/
│               └── nodes/
│                   └── identify_topics/
│                       └── test_identify_topics.py   # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión de la estructura 003. Nuevo nodo `identify_topics` autocontenido (Principio II). El grafo pasa de `preprocess → extract_participants → mock_result` a `preprocess → extract_participants → identify_topics → mock_result`. mock_result deja de incluir `topics` en su retorno para preservar el valor extraído por identify_topics. La UI ya tiene `show_progress=True` en el botón Procesar; si el loader no es suficientemente visible, añadir componente de carga explícito según skill gradio.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
