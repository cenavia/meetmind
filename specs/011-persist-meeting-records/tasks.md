# Tasks: Almacenamiento persistente de reuniones procesadas

**Input**: Design documents from `/specs/011-persist-meeting-records/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos — el plan y la constitución exigen pruebas en `tests/unit/db/` y `tests/integration/api/` para repositorio y flujo API.

**Organization**: Fases alineadas a user stories de spec.md (US1 P1, US2/US3 P2).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos distintos, sin depender de tareas incompletas del mismo bloque)
- **[Story]**: Solo en fases de user story (US1, US2, US3)
- Incluir en cada descripción la ruta **relativa a la raíz del repositorio** `meetmind/` (p. ej. `src/...`, `tests/...`)

## Path Conventions

- Monorepo: `src/`, `tests/` en la raíz de `meetmind/` (rutas en tareas relativas a esa raíz)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencias y documentación de entorno para SQLModel/SQLite

- [x] T001 Add `sqlmodel` (y dependencia transitiva SQLAlchemy) to `pyproject.toml` dependencies array
- [x] T002 [P] Uncomment or add active `DATABASE_URL=sqlite:///./meetmind.db` with short comment in `.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Motor, modelo `MeetingRecord`, repositorio y sesión inyectable en FastAPI — **bloquea todas las user stories**

**⚠️ CRITICAL**: No implementar persistencia en rutas `/process` hasta completar esta fase

- [x] T003 Create package marker `src/db/__init__.py`
- [x] T004 Implement `create_engine`, `Session` factory, and `init_db()` / table creation in `src/db/database.py` (support SQLite default URL; compatible with standard SQLAlchemy URLs)
- [x] T005 Define table model `MeetingRecord` (fields per `specs/011-persist-meeting-records/data-model.md`: id UUID PK, text fields, optional source_file_name/source_file_type, status enum, created_at, processing_errors) in `src/db/models.py` (después de T004; no marcar [P] frente a T004)
- [x] T006 Implement `MeetingRepository` with `create(...)`, `get_by_id(uuid)`, `list_all_by_created_desc()` in `src/db/repository.py`
- [x] T007 Add `get_database_url()` (default `sqlite:///./meetmind.db` when `DATABASE_URL` unset) in `src/config.py`
- [x] T008 Call DB initialization from app `lifespan` in `src/api/main.py` (create tables on startup for MVP)
- [x] T009 Add FastAPI dependencies `get_db_session` generator and `get_meeting_repository` in `src/api/dependencies.py`

**Checkpoint**: Arranque de API sin error; tablas creadas; sesión y repositorio inyectables en un endpoint de prueba manual si hace falta

---

## Phase 3: User Story 1 — Guardar reunión al terminar el procesamiento (Priority: P1) 🎯 MVP

**Goal**: Cada ejecución que termina con resultado del grafo o fallo terminal acordado deja un registro durable (FR-001, FR-011)

**Independent Test**: Tras `POST /api/v1/process/text` con texto válido, existe fila nueva con UUID; reinicio de API y consulta (cuando US2 exista) devuelve mismos datos — o verificación SQL directa hasta entonces

### Implementation for User Story 1

- [x] T010 [US1] After successful `graph.invoke` in `src/api/routers/process.py`, persist a new `MeetingRecord` via repository (`Depends`): map `ProcessMeetingResponse` fields; `source_file_name`/`source_file_type` null for text route; asignar `status`: `partial` si el dict devuelto por el grafo tiene `processing_errors` no vacío **o** si `minutes`/`executive_summary` incluyen el prefijo de salida limitada del PRD (`[Información limitada]`); en caso contrario `completed` (T014 mejora el primer criterio propagando errores desde nodos)
- [x] T011 [US1] After successful `graph.invoke` in `src/api/routers/process.py` for `POST /file` branches (text and multimedia), persist with filename and content type/extension when available; misma regla `completed`/`partial` que T010
- [x] T012 [US1] On SSE `type: complete` in `src/api/process_file_stream.py`, persist the same way for text and file streams (mirror sync route behavior); misma regla `completed`/`partial` que T010
- [x] T013 [US1] On terminal transcription/processing failure after pipeline started (e.g. `TranscriptionError`, timeout) in `src/api/routers/process.py` and `src/api/process_file_stream.py`, persist `failed` row with `processing_errors` message and empty result fields where applicable per research.md. **No persistir** en errores solo de validación previa al pipeline acordados con research: p. ej. texto vacío, archivo sin nombre, 415 por tipo no soportado, texto que supera el límite de caracteres, archivo que supera el tamaño máximo (solo rechazo HTTP, sin fila).

### Mejora recomendada (FR-004, paralelizable con precaución)

- [x] T014 [P] [US1] Add `processing_errors` to `MeetingState` in `src/agents/meeting/state.py` and set from nodos cuando aplique entrada limitada o advertencias según PRD 12.4 / constitución IV, para que el API persista `partial` con mensajes sin depender solo del prefijo en minuta/resumen

**Checkpoint**: Procesamiento vía REST y SSE crea registros; fallos de transcripción pueden crear `failed` según decisiones de research.md

---

## Phase 4: User Story 2 — Consultar una reunión por su identificador (Priority: P2)

**Goal**: `GET /api/v1/meetings/{meeting_id}` devuelve 200 con cuerpo completo o 404 claro (FR-006, SC-004)

**Independent Test**: `curl` GET por UUID existente vs inventado según `specs/011-persist-meeting-records/contracts/meetings-api.md`

### Implementation for User Story 2

- [x] T015 [US2] Create `src/api/routers/meetings.py` with Pydantic `MeetingRecordResponse` matching contract (snake_case, ISO datetime, nullable fields)
- [x] T016 [US2] Implement `GET /meetings/{meeting_id}` in `src/api/routers/meetings.py` parsing UUID, 404 Spanish detail when missing
- [x] T017 [US2] Register `meetings` router with prefix `/api/v1` in `src/api/main.py` (path `/meetings` as in contract)

**Checkpoint**: GET por id verificable con curl tras US1

---

## Phase 5: User Story 3 — Listar reuniones guardadas (Priority: P2)

**Goal**: `GET /api/v1/meetings` devuelve todas las filas ordenadas por `created_at` descendente (FR-007, SC-002)

**Independent Test**: Tras varias ejecuciones, listado incluye todas y orden correcto según contract

### Implementation for User Story 3

- [x] T018 [US3] Implement `GET /meetings` returning `{ "items": [...] }` in `src/api/routers/meetings.py` using `MeetingRepository.list_all_by_created_desc()`

**Checkpoint**: Historial básico operativo sin paginación

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Calidad, pruebas automatizadas y alineación con quickstart

- [x] T019 [P] Add unit tests for `MeetingRepository` (create, get missing, list order) using SQLite file or in-memory URL in `tests/unit/db/test_meeting_repository.py`
- [x] T020 Add integration tests in `tests/integration/api/test_meetings_persist.py` (`TestClient`, BD SQLite en fichero temporal vía `DATABASE_URL` o fixture): **(1)** flujo básico: `POST /api/v1/process/text` → `GET /api/v1/meetings/{id}` y `GET /api/v1/meetings` con datos coherentes; **(2) SC-002**: crear ≥5 registros (textos distintos o `sleep` mínimo si hace falta para `created_at` distintos), `GET /meetings` debe devolver 5+ ítems en orden `created_at` descendente; **(3) SC-001**: tras un `POST` exitoso, cerrar/desechar el engine o la app del primer `TestClient` y levantar una **nueva** app apuntando al **mismo** fichero SQLite, luego `GET /meetings/{id}` debe coincidir con lo guardado (simula reinicio); **(4) SC-003** (suave): opcional `pytest.mark` o aserción no estricta — tiempo entre POST y primer GET menor de 5 segundos en entorno local, marcar skip en CI si es ruidoso
- [x] T021 Align `docs/planning/COMO-EJECUTAR.md` or README snippet with `DATABASE_URL` and verificación rápida si aplica (keep minimal)
- [x] T022 [P] Run through manual steps in `specs/011-persist-meeting-records/quickstart.md` and fix gaps in code or doc; si T020 no cubre reinicio real con uvicorn, validar SC-001 manualmente (stop/start API + mismo `meetmind.db`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** → **Phase 2** → **Phases 3–5** (US1 puede antes que US2/US3 en tiempo, pero US2/US3 necesitan datos: en la práctica completar US1 o al menos T010–T012 antes de validar US2/US3 con contenido real)
- **US2** y **US3**: ambas requieren Phase 2; US3 puede implementarse inmediatamente después de US2 en el mismo archivo
- **Phase 6** después de US1–US3 (o al menos tras US1 para tests de persistencia parciales)

### User Story Dependencies

- **US1**: Depende de Phase 2; no depende de US2/US3 para implementación (solo para prueba cómoda vía GET)
- **US2**: Depende de Phase 2 y de existir al menos un registro para prueba end-to-end (típicamente US1 hecha)
- **US3**: Igual que US2; orden lógico US2 → US3 en el mismo router

### Parallel Opportunities

- T002 y T001 en Phase 1 (archivos distintos)
- Phase 2: T004 → T005 → T006 en secuencia recomendada (T005 no [P] respecto a T004)
- T019 y T021 en Phase 6 en paralelo
- T014 en paralelo con T010–T013 solo si se evitan conflictos de merge (`state.py` vs routers)

---

## Parallel Example: User Story 1

```bash
# Tras Phase 2, en paralelo solo si hay cuidado con conflictos de merge:
# - T014: src/agents/meeting/state.py
# - (T010–T013 comparten process.py / process_file_stream.py → secuencial)
```

---

## Parallel Example: Phase 6

```bash
# En paralelo:
# T019 tests/unit/db/test_meeting_repository.py
# T021 docs/planning/COMO-EJECUTAR.md
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 + Phase 2  
2. Phase 3 (US1) — validar con SQLite/browser o SQL directo  
3. Parar y demostrar persistencia tras reinicio (SC-001) usando inspección de BD hasta tener US2  

### Incremental Delivery

1. Setup + Foundational  
2. US1 → persistencia completa en flujos síncronos y SSE  
3. US2 → GET por id  
4. US3 → listado  
5. Polish → tests + quickstart  

### Suggested MVP Scope

- **Mínimo**: Phase 1–3 (T001–T013) + inspección manual de BD  
- **Producto usable con spec**: Añadir Phase 4–5 (T015–T018)  

---

## Notes

- No añadir autenticación ni DELETE en esta lista (fuera de alcance FR-009/FR-010).  
- Cada tarea debe poder ejecutarse con el contexto de `plan.md` + `contracts/meetings-api.md` + `data-model.md`.  
- IDs secuenciales T001–T022; marcar [P] solo donde no haya dependencia de salida de otra tarea incompleta.
