# Implementation Plan: Almacenamiento persistente de reuniones procesadas

**Branch**: `011-persist-meeting-records` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/011-persist-meeting-records/spec.md`

## Summary

Introducir persistencia durable de cada **ejecución** del workflow de reunión mediante **SQLModel** y un almacén relacional (SQLite por defecto, PostgreSQL vía `DATABASE_URL`). Tras cada terminación relevante del procesamiento, la **capa API** crea un registro con UUID, campos de resultado alineados al PRD (`participants`, `topics`, `actions`, `minutes`, `executive_summary` como columna/API homónima al `ProcessMeetingResponse` actual), metadatos opcionales de archivo, `status` (`completed` \| `failed` \| `partial`), `created_at` y `processing_errors`. Exponer **GET** por id y **GET** listado ordenado por `created_at` descendente. La escritura se orquesta desde FastAPI (post-`invoke` o error terminal tras inicio del pipeline), **sin** meter acceso a BD dentro de nodos LangGraph. Autenticación explícita fuera de alcance (FR-009); asumir entorno de confianza.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy 2.x, LangGraph (sin cambio de forma del grafo obligatorio), Pydantic v2  
**Storage**: SQLite (`sqlite:///./meetmind.db` por defecto si `DATABASE_URL` no está definida) o PostgreSQL/MySQL según URL estándar SQLAlchemy  
**Testing**: pytest — unitarios en `tests/unit/db/` (repositorio, modelo); integración en `tests/integration/api/` (persistencia tras proceso + GET/list)  
**Target Platform**: Servidor API (uvicorn), mismo despliegue actual de MeetMind  
**Project Type**: Web service (API FastAPI + persistencia)  
**Performance Goals**: Alineado a SC-003 de la spec: registro recuperable en menos de 5 segundos tras confirmación de guardado en uso típico  
**Constraints**: Sin authN/Z en producto para lecturas; sin TTL ni DELETE en alcance (FR-010); cada `invoke` exitoso → nuevo registro (FR-011); listado completo sin paginación en esta historia  
**Scale/Scope**: Nuevo paquete `src/db/` (engine, sesión, modelo `MeetingRecord`, repositorio); nuevas rutas REST; tocar `process.py` / `process_file_stream.py` para invocar persistencia en puntos de salida; opcional extender `MeetingState` con `processing_errors` si se centraliza el estado parcial en el grafo (ver research.md)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Persistencia invocada desde **API** tras orquestar el grafo; Gradio solo consume API; nodos sin SQL |
| II. Nodos autocontenidos | ✅ | No se añade lógica de BD en `agents/meeting/nodes/`; opcional campo en `state` solo si mejora trazabilidad sin acoplar a DB |
| III. Formatos de salida estructurados | ✅ | Columnas de texto respetan mismos formatos que `ProcessMeetingResponse` / PRD |
| IV. Robustez ante información incompleta | ✅ | Registros `failed` / `partial` con `processing_errors` y campos vacíos cuando aplique |
| V. Modularidad y testabilidad | ✅ | Repositorio testeable; `Depends` para sesión/repo; tests `tests/unit/db/` |
| VI. Agent Skills | ✅ | Consultar `fastapi`, `langgraph-fundamentals`, `langchain-dependencies` al implementar |

**Gates**: PASS. Sin violaciones; sin filas en Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/011-persist-meeting-records/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1 (API meetings)
└── tasks.md             # Phase 2 (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── api/
│   │   ├── main.py                 # MODIFICAR: lifespan → init engine/create tables (o migraciones futuras)
│   │   ├── dependencies.py         # MODIFICAR: get_db_session, get_meeting_repository (o similar)
│   │   ├── routers/
│   │   │   ├── process.py          # MODIFICAR: tras graph.invoke (y errores terminales acordados) → persist
│   │   │   └── meetings.py         # CREAR: GET /meetings, GET /meetings/{id}
│   │   └── process_file_stream.py  # MODIFICAR: en rama complete / error terminal → persist
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py             # CREAR: engine, session factory, init
│   │   ├── models.py               # CREAR: MeetingRecord (SQLModel table=True)
│   │   └── repository.py           # CREAR: create, get_by_id, list_recent_first
│   ├── agents/meeting/
│   │   └── state.py                # OPCIONAL: processing_errors en MeetingState si se unifica con grafo
│   └── config.py                   # MODIFICAR: DATABASE_URL opcional con default SQLite
│
├── tests/
│   ├── unit/db/                    # CREAR: test_repository, test_models
│   └── integration/api/            # CREAR o ampliar: persistencia + GET tras POST process
│
├── .env.example                    # MODIFICAR: documentar DATABASE_URL activa
└── pyproject.toml                  # Verificar dependencias SQLModel/SQLAlchemy
```

**Structure Decision**: Monorepo single backend. Persistencia en `src/db/` según constitución. Los endpoints de lectura viven en un router dedicado bajo el prefijo existente `/api/v1`.

## Complexity Tracking

> Sin violaciones de constitución en este plan.

## Phase 0 & 1 outputs

| Artefacto | Ruta |
|-----------|------|
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| Contracts | [contracts/meetings-api.md](./contracts/meetings-api.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

### Post Phase 1 — Constitution re-check

Los contratos mantienen la separación API/negocio; el modelo de datos no expone detalles del grafo en la respuesta pública más allá de los campos ya acordados. **Gates**: PASS.
