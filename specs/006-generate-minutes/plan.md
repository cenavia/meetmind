# Implementation Plan: Ver minuta formal

**Branch**: `006-generate-minutes` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/006-generate-minutes/spec.md`

## Summary

Implementar el nodo `generate_minutes` que genera una minuta formal en español a partir de participantes, temas y acciones ya extraídos. La minuta es texto narrativo continuo, tono profesional, máximo 150 palabras (conteo: split por espacios). Cuando no hay datos de entrada: mensaje fijo "Minuta: No se identificó información procesable en la reunión." Si el LLM excede 150 palabras: truncamiento post-proceso preservando coherencia. El nodo se inserta entre `extract_actions` y `mock_result`. `mock_result` deja de devolver `minutes`; el campo se popula con la salida de `generate_minutes`.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Gradio, LangGraph, LangChain (langchain-core), uv  
**Storage**: N/A (sin persistencia para esta feature)  
**Testing**: pytest (tests unitarios para generate_minutes, integración para flujo completo)  
**Target Platform**: Linux/macOS (desarrollo local)  
**Project Type**: Web application (API + UI)  
**Performance Goals**: Generación de minuta como parte del pipeline; tiempo total alineado con 001-005  
**Constraints**: minutes ≤150 palabras; formato texto narrativo; español; caso vacío: mensaje fijo  
**Scale/Scope**: Un nodo adicional en el grafo; mock_result deja de proporcionar minutes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Nodo en Core; API sin cambios; UI hereda presentación existente |
| II. Nodos autocontenidos | ✅ | generate_minutes en `nodes/generate_minutes/` con node.py y prompt.py |
| III. Formatos de salida | ✅ | minutes: str, máx. 150 palabras; PRD Anexo A/B |
| IV. Robustez ante información incompleta | ✅ | Sin datos → mensaje fijo estándar; info parcial → minuta con lo disponible; truncamiento si >150 palabras |
| V. Modularidad y testabilidad | ✅ | Nodo testeable aislado; prompts en módulo separado |
| VI. Agent Skills | ✅ | langgraph-fundamentals, langchain-fundamentals |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/006-generate-minutes/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (minutes field format)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   └── agents/
│       └── meeting/
│           ├── agent.py                          # MODIFICAR: añadir generate_minutes, edge extract_actions→generate_minutes→mock_result
│           ├── state.py                          # Sin cambios (minutes ya existe)
│           └── nodes/
│               ├── preprocess/
│               ├── extract_participants/
│               ├── identify_topics/
│               ├── extract_actions/
│               ├── generate_minutes/             # CREAR
│               │   ├── __init__.py
│               │   ├── node.py                   # Lógica: detectar vacío→mensaje fijo; LLM→narrativa; post-proceso 150 palabras
│               │   └── prompt.py                 # Prompt especializado
│               └── mock_result/
│                   └── node.py                   # MODIFICAR: no devolver minutes (usa valor de state)
│
├── tests/
│   └── unit/
│       └── agents/
│           └── meeting/
│               └── nodes/
│                   └── generate_minutes/
│                       └── test_generate_minutes.py   # CREAR
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión del grafo existente. Nuevo nodo `generate_minutes` autocontenido (Principio II). El grafo pasa de `... → extract_actions → mock_result` a `... → extract_actions → generate_minutes → mock_result`. mock_result deja de incluir `minutes` en su retorno para preservar el valor generado por generate_minutes.

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
