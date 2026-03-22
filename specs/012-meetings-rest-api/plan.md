# Implementation Plan: API HTTP de procesamiento y consulta de reuniones (US-010)

**Branch**: `012-meetings-rest-api` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/012-meetings-rest-api/spec.md`

## Summary

Formalizar y completar la **API REST pública** alineada con US-010 y las clarificaciones de sesión: rutas versionadas bajo `/api/v1` para procesamiento (texto y archivo), listado y detalle de reuniones, **liveness** y **readiness**, documentación OpenAPI en `/docs`, códigos HTTP coherentes (validación 4xx, servidor 5xx sin fugas), **persistencia obligatoria tras éxito** cuando la BD está activa, procesamiento **síncrono**, y **FR-014**: fallo de almacenamiento en lectura → error de servidor inequívoco (no listado vacío ni 404 “fantasma”). El código ya cubre buena parte (`process`, `meetings`, `/health`); este plan cierra brechas (readiness, manejo de errores de BD en GET, posible `meeting_id` en respuesta POST, política si falla persist tras grafo OK).

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLModel/SQLAlchemy 2.x, LangGraph (invocado solo desde la capa API)  
**Storage**: SQLite por defecto / URL SQLAlchemy (`DATABASE_URL`) — mismo modelo `MeetingRecord` que 011  
**Testing**: pytest — `tests/integration/api/` (contrato HTTP, códigos, liveness/readiness); ampliar unitarios si se extraen helpers de errores  
**Target Platform**: Servidor ASGI (uvicorn), mismo despliegue MeetMind  
**Project Type**: Web service (API REST)  
**Performance Goals**: Liveness < 2 s en p95 (SC-005 spec 012); procesamiento síncrono acotado por `get_processing_timeout_sec` y límites de cliente  
**Constraints**: Sin authN/Z en producto; CORS configurable (hoy `*` en `main.py`); no exponer trazas en respuestas; validación MIME/tamaño ya en `multimedia_validation`  
**Scale/Scope**: Sin paginación en listado en esta historia; sin jobs asíncronos (FR-013)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | Endpoints solo orquestan grafo + repo; sin SQL en nodos |
| II. Nodos autocontenidos | ✅ | Sin cambios al grafo obligatorios |
| III. Formatos de salida estructurados | ✅ | `ProcessMeetingResponse` / `MeetingRecordResponse` alineados PRD |
| IV. Robustez ante información incompleta | ✅ | 422/400 en validación; errores parciales ya modelados en `status` |
| V. Modularidad y testabilidad | ✅ | Routers + `Depends`; tests de integración por endpoint |
| VI. Agent Skills | ✅ | Consultar `fastapi` al implementar rutas y manejo de errores |

**Gates**: PASS. Sin filas en Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/012-meetings-rest-api/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md              # /speckit.tasks (no creado por este comando)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── api/
│   │   ├── main.py                 # MODIFICAR: registrar readiness si nuevo router; CORS/docs ya OK
│   │   ├── dependencies.py         # REUTILIZAR: get_db_session, get_meeting_repository
│   │   ├── routers/
│   │   │   ├── health.py           # MODIFICAR: mantener /health (liveness); añadir /ready (readiness)
│   │   │   ├── process.py          # REVISAR: fallo persist tras éxito → no 200 silencioso (FR-012)
│   │   │   └── meetings.py         # MODIFICAR: capturar errores BD → 503 (FR-014), no vacío/404 falso
│   │   └── multimedia_validation.py
│   ├── db/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   └── agents/meeting/
├── tests/integration/api/          # AMPLIAR: health, meetings errors, proceso + id opcional
└── .env.example
```

**Structure Decision**: Monorepo backend único; routers existentes se extienden. Contratos en `specs/012-meetings-rest-api/contracts/`.

## Complexity Tracking

> Sin violaciones de constitución. Ninguna fila obligatoria.

## Phase 0 & 1 outputs

| Artefacto | Ruta |
|-----------|------|
| Research | [research.md](./research.md) |
| Data model | [data-model.md](./data-model.md) |
| Contracts | [contracts/openapi-rest.md](./contracts/openapi-rest.md) |
| Quickstart | [quickstart.md](./quickstart.md) |

### Post Phase 1 — Constitution re-check

Los contratos mantienen la API como fachada; el grafo no se expone. **Gates**: PASS.
