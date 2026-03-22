# Tasks: API HTTP de procesamiento y consulta de reuniones (012-meetings-rest-api)

**Input**: Design documents from `/specs/012-meetings-rest-api/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/openapi-rest.md](./contracts/openapi-rest.md), [quickstart.md](./quickstart.md)

**Tests**: Incluidas tareas de integración acotadas alineadas al plan (pytest `tests/integration/`). No se exige TDD estricto en la spec; ejecutar suite al final.

**Organization**: Fases por historia de usuario de [spec.md](./spec.md); orden P1 → P2 → P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Paralelizable (archivos distintos, sin dependencia de tareas incompletas del mismo lote)
- **[USn]**: Historia de usuario (US1…US5)
- Rutas: raíz del repositorio MeetMind

---

## Phase 1: Setup (infraestructura mínima)

**Purpose**: Alinear documentación y dependencias antes de tocar código compartido.

- [x] T001 Revisar coherencia entre `specs/012-meetings-rest-api/contracts/openapi-rest.md` y rutas actuales en `src/api/` (anotar desviaciones a corregir en fases siguientes)
- [x] T002 [P] Verificar que `pyproject.toml` incluye dependencias necesarias (FastAPI, SQLModel, SQLAlchemy, httpx para tests) sin cambios si ya cumple

---

## Phase 2: Foundational (prerrequisitos bloqueantes)

**Purpose**: Utilidad de comprobación de BD reutilizable por readiness (y opcionalmente tests).

**⚠️ CRITICAL**: Completar antes de implementar `GET /ready` y pruebas que dependan del ping.

- [x] T003 Implementar función de ping a BD (p. ej. `check_database_connectivity()` usando `Session`/`engine` existente) en `src/db/database.py` con manejo de excepciones claro
- [x] T004 Exponer uso previsto en docstrings de `src/db/database.py` para operadores (liveness vs readiness)

**Checkpoint**: Ping de BD invocable sin levantar FastAPI (import directo o test unitario mínimo opcional)

---

## Phase 3: User Story 1 — Procesar reunión enviando texto (Priority: P1) 🎯 MVP

**Goal**: `POST /api/v1/process/text` síncrono, validación clara, persistencia tras éxito (FR-012), `meeting_id` en respuesta cuando aplique, 503 si persistencia falla tras grafo OK (research §4).

**Independent Test**: `curl` o cliente HTTP: texto válido → 200 con cinco campos + `meeting_id` no nulo si BD activa; persistencia rota simulada → no 200 “exitoso” completo según política acordada.

### Implementation for User Story 1

- [x] T005 [US1] Extender modelo `ProcessMeetingResponse` con campo opcional `meeting_id: UUID | None = None` en `src/api/routers/process.py`
- [x] T006 [US1] Sustituir `_try_persist_success` por flujo que obtenga `MeetingRecord` desde `persist_graph_success`/`repo.create_record`: asignar `meeting_id` en la respuesta; si falla persistencia tras `graph.invoke` exitoso, lanzar `HTTPException(503, detail=...)` en lugar de devolver 200 en `process_text` en `src/api/routers/process.py` (ajustar `src/db/meeting_persist.py` si debe retornar el registro creado)
- [x] T007 [US1] Añadir `summary`/`description` OpenAPI al endpoint `POST /text` en `src/api/routers/process.py` (FR-009)

**Checkpoint**: US1 verificable sin archivo multipart

---

## Phase 4: User Story 2 — Procesar reunión enviando archivo (Priority: P1)

**Goal**: `POST /api/v1/process/file` (y flujos asociados) con la misma política de persistencia y `meeting_id` que US1; validación MIME/tamaño existente intacta.

**Independent Test**: Multipart con archivo permitido → 200 + campos + `meeting_id`; archivo inválido → 4xx con `detail` claro.

### Implementation for User Story 2

- [x] T008 [US2] Alinear `process_file` en `src/api/routers/process.py` con retorno de `meeting_id` y `HTTPException(503)` si falla persistencia tras resultado listo (misma política que `process_text`)
- [x] T009 [US2] Revisar `src/api/process_file_stream.py` y cualquier rama que llame a persistencia: no devolver evento `complete` con éxito si la persistencia obligatoria falla cuando la BD está activa (alinear con research §4 y FR-012)
- [x] T010 [US2] Mejorar descripciones OpenAPI en endpoints de archivo en `src/api/routers/process.py`

**Checkpoint**: US1 y US2 coherentes en contrato de respuesta y errores de persistencia

---

## Phase 5: User Story 3 — Liveness y readiness (Priority: P2)

**Goal**: `GET /health` solo liveness; `GET /ready` comprueba BD; respuestas y códigos distinguibles (FR-005, SC-009).

**Independent Test**: `/health` 200 sin BD; con BD caída `/ready` → 503 y `/health` puede seguir 200.

### Implementation for User Story 3

- [x] T011 [US3] Documentar en docstrings que `GET /health` es liveness (sin BD) en `src/api/routers/health.py`
- [x] T012 [US3] Implementar `GET /ready` en `src/api/routers/health.py` usando `check_database_connectivity()` de `src/db/database.py` (o `Depends` + sesión); 200 si OK, 503 con `detail` claro si falla
- [x] T013 [US3] Confirmar registro de rutas en `src/api/main.py` (`include_router(health.router)` ya incluye ambas rutas si viven en el mismo router)

**Checkpoint**: Operador puede distinguir vivo vs preparado vía dos URLs

---

## Phase 6: User Story 4 — Historial y detalle (Priority: P2)

**Goal**: `GET /api/v1/meetings` y `GET /api/v1/meetings/{id}` con FR-014 (fallo BD → 503, no listado vacío ni 404 “falso”).

**Independent Test**: Con BD normal, listado y 404 por id inexistente; con fallo de lectura simulado, respuesta 503 inequívoca.

### Implementation for User Story 4

- [x] T014 [US4] Envolver `list_meetings` y `get_meeting` con captura de excepciones SQLAlchemy/DBAPI apropiadas y `HTTPException(503, detail=...)` en `src/api/routers/meetings.py` sin devolver `items: []` por fallo de almacén
- [x] T015 [US4] Documentar en OpenAPI (`response_description` o docstrings) códigos 200/404/503 para ambos endpoints en `src/api/routers/meetings.py`

**Checkpoint**: US4 alineado con contrato `contracts/openapi-rest.md`

---

## Phase 7: User Story 5 — Documentación de interfaz (Priority: P3)

**Goal**: `/docs` y metadatos de la app reflejan operaciones, tags y propósito liveness/readiness (FR-009).

**Independent Test**: Abrir `/docs` y localizar process, meetings, health, ready con descripciones útiles.

### Implementation for User Story 5

- [x] T016 [US5] Actualizar `title`/`description`/`version` y tags globales si aplica en `src/api/main.py` para reflejar API v1, procesamiento y salud
- [x] T017 [US5] Revisar `tags=` en routers `src/api/routers/health.py`, `src/api/routers/process.py`, `src/api/routers/meetings.py` para consistencia en OpenAPI

**Checkpoint**: Integrador encuentra todas las operaciones sin leer código fuente

---

## Phase 8: Polish & cross-cutting

**Purpose**: Tests, clientes y validación final.

- [x] T018 [P] Añadir o ampliar pruebas de integración para `GET /health` y `GET /ready` en `tests/integration/api/test_health_ready.py`
- [x] T019 [P] Ampliar `tests/integration/api/test_meetings_persist.py` (o nuevo archivo) para asertar `meeting_id` en respuesta `POST /process/text` cuando proceda
- [x] T020 [P] Añadir prueba de integración que mockea o fuerza error de BD en listado/detalle y espera 503 en `tests/integration/api/test_meetings_db_errors.py` (usar patrón del proyecto: fixture, dependency override o URL inválida según viabilidad)
- [x] T021 Ejecutar `uv run pytest tests/integration/` desde la raíz del repositorio y corregir regresiones en tests existentes que asuman forma estricta de `ProcessMeetingResponse`
- [x] T022 Verificar que `src/ui/app.py` sigue funcionando con campo extra `meeting_id` (solo usa claves conocidas en `_format_result`); ajustar solo si hay validación estricta del JSON
- [x] T023 [P] Sincronizar `specs/012-meetings-rest-api/quickstart.md` con nombre real del campo multipart (`file` u otro) según `src/api/routers/process.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** → **Phase 2** → **Phases 3–7** (US1→US2→US3→US4→US5 recomendado por solapamiento en `process.py`) → **Phase 8**
- **US3** puede empezar tras Phase 2 en paralelo con US1 si se coordinan archivos distintos; **US4** independiente tras Phase 2. Orden secuencial seguro: 3 → 4 → 5 → 6 → 7.

### User Story Dependencies

| Story | Depende de |
|-------|------------|
| US1 | Phase 2 (opcional ping reutilizado solo en US3; US1 no lo requiere) |
| US2 | US1 recomendado (misma política de respuesta en `process.py`) |
| US3 | Phase 2 (ping BD) |
| US4 | Phase 2 (manejo errores; sin dependencia de US1) |
| US5 | Preferible tras endpoints estables (fases 3–6) |

### Parallel Opportunities

- T002 paralelo a T001
- T018, T019, T020, T023 en Phase 8 en paralelo si no compiten por los mismos archivos
- US3 (health) y US4 (meetings) pueden desarrollarse en paralelo tras Phase 2 (archivos distintos)

---

## Parallel Example: User Story 3 + User Story 4

Tras completar Phase 2, un desarrollador puede trabajar `src/api/routers/health.py` (T011–T013) mientras otro trabaja `src/api/routers/meetings.py` (T014–T015), coordinando solo convenciones de mensajes `detail` en español.

---

## Implementation Strategy

### MVP (US1 sola)

1. Phase 1–2 ligeras (T001–T004 según necesidad; T003–T004 mínimas para readiness posterior)
2. Phase 3 completa (T005–T007)
3. Validar con `POST /process/text` y persistencia

### Entrega incremental

1. US1 + US2 (procesamiento completo)
2. US3 + US4 (operación y lectura fiables)
3. US5 + Polish (documentación y tests)

---

## Notes

- `persist_graph_success` hoy retorna `None`: la tarea T006/T008 implica refactor menor para devolver `MeetingRecord` o consultar id tras `create_record`.
- No añadir autenticación en este backlog (FR-010 spec).
- Cumplir skill `fastapi` del proyecto al implementar excepciones y modelos de respuesta.
