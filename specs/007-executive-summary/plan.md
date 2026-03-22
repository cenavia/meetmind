# Implementation Plan: Ver resumen ejecutivo

**Branch**: `007-executive-summary` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/007-executive-summary/spec.md`

## Summary

Implementar el nodo `create_summary` que genera un resumen ejecutivo de máximo 30 palabras en español a partir de toda la información procesada (participantes, temas, acciones, minuta). El resumen se enfoca en decisiones, acciones críticas y conclusiones principales. Cuando no hay datos de entrada: mensaje fijo "Resumen: No se identificó información procesable en la reunión." Si el LLM excede 30 palabras: retry con prompt ajustado hasta cumplir el límite. El nodo se inserta entre `generate_minutes` y `mock_result`. `mock_result` deja de devolver `executive_summary`; el campo se popula con la salida de `create_summary`. Además, la UI Gradio debe desactivar el botón «Procesar» inmediatamente al hacer clic y mantenerlo desactivado hasta que el usuario haga clic en «Limpiar».

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (sin persistencia para esta feature)  
**Testing**: pytest (tests unitarios para create_summary, integración para flujo completo; tests UI para botón Procesar)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Generación de resumen como parte del pipeline; tiempo total alineado con 001-006  
**Constraints**: summary ≤30 palabras; español; caso vacío: mensaje fijo; retry si LLM excede; Procesar desactivado hasta Limpiar  
**Scale/Scope**: Un nodo adicional en el grafo; ajuste en mock_result; cambios en UI Gradio (botón Procesar)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Nodo en Core; API sin cambios; UI solo cambios en estado del botón (sin lógica de negocio) |
| II. Nodos autocontenidos | ✅ | create_summary en `nodes/create_summary/` con node.py y prompt.py |
| III. Formatos de salida | ✅ | executive_summary: str, máx. 30 palabras; PRD Anexo A/B |
| IV. Robustez ante información incompleta | ✅ | Sin datos → mensaje fijo; retry si >30 palabras; UI: Procesar desactivado evita clics repetidos |
| V. Modularidad y testabilidad | ✅ | Nodo testeable aislado; prompts en módulo separado; UI testeable |
| VI. Agent Skills | ✅ | langgraph-fundamentals, langchain-fundamentals, gradio |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/007-executive-summary/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (summary field)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── agents/
│   │   └── meeting/
│   │       ├── agent.py                          # MODIFICAR: añadir create_summary, edge generate_minutes→create_summary→mock_result
│   │       └── nodes/
│   │           ├── generate_minutes/
│   │           ├── create_summary/               # CREAR
│   │           │   ├── __init__.py
│   │           │   ├── node.py                   # Lógica: detectar vacío→mensaje fijo; LLM→resumen; retry si >30 palabras
│   │           │   └── prompt.py                 # Prompt especializado (decisiones, acciones, conclusiones)
│   │           └── mock_result/
│   │               └── node.py                   # MODIFICAR: no devolver executive_summary (usa valor de state)
│   │
│   └── ui/
│       └── app.py                                # MODIFICAR: Procesar se desactiva al clic; Limpiar reactiva flujo
│
├── tests/
│   └── unit/
│       └── agents/
│           └── meeting/
│               └── nodes/
│                   └── create_summary/
│                       └── test_create_summary.py   # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión del grafo existente. Nuevo nodo `create_summary` autocontenido (Principio II). El grafo pasa de `... → generate_minutes → mock_result` a `... → generate_minutes → create_summary → mock_result`. mock_result deja de incluir `executive_summary` en su retorno. La UI Gradio modifica el handler de `process_btn.click` para desactivar el botón al procesar y añadir `process_btn` a los outputs; `clear_btn` ya restablece el flujo y, al cargar nuevo contenido, `update_inputs` reactiva el botón.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
