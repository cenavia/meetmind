# Tasks: Feedback ante información incompleta y errores (US-011 / spec 013)

**Input**: Design documents from `/specs/013-incomplete-error-feedback/`  
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/processing-feedback.md](./contracts/processing-feedback.md), [quickstart.md](./quickstart.md)

**Tests**: Incluidos — el plan y la constitución exigen pruebas en `tests/unit/` y `tests/integration/api/` para codec, preprocess y forma de respuesta HTTP.

**Organization**: Fases alineadas a prioridades de spec.md (US1–US2 P1, US3–US4 P2, US5 P3).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos distintos, sin depender de tareas incompletas del mismo bloque)
- **[Story]**: Solo en fases de user story (`US1` … `US5`)
- Rutas relativas a la raíz del repositorio `meetmind/`

## Path Conventions

- Monorepo: `src/`, `tests/` en la raíz de `meetmind/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Configuración mínima para umbral de “texto corto” alineado a research/spec

- [x] T001 Add `get_meeting_min_words()` (default **20**, override opcional vía env p. ej. `MEETING_MIN_WORDS`) in `src/config.py` y documentar en `.env.example` si aplica

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estado del grafo como **lista**, serialización BD, DTOs API y SSE coherentes — **bloquea todas las user stories**

**⚠️ CRITICAL**: No cerrar tareas de UI que consuman `processing_errors` hasta que T002–T009 estén consistentes

- [x] T002 Define `MeetingState` con `processing_errors` como acumulación por **lista** (`Annotated[list[str], operator.add]` o patrón equivalente en LangGraph) in `src/agents/meeting/state.py` y configura el grafo en `src/agents/meeting/agent.py` para que los nodos no pisen advertencias previas
- [x] T003 Implement `encode_processing_errors` / `decode_processing_errors` (JSON array en `Text`, decodificación tolerante a filas legacy texto plano) in `src/db/processing_errors_codec.py`
- [x] T004 Refactor `src/db/meeting_persist.py`: leer `processing_errors` del dict del grafo como `list[str]`; serializar con T003 antes de `repository.create_record`; actualizar `status_from_graph_result` para listas vacías/no vacías y reglas `completed`/`partial`; hacer que `persist_failed` acepte mensaje único o lista y persista codificado sin fugas técnicas
- [x] T005 Update every meeting node that touches `processing_errors` to return **list fragments** only: `src/agents/meeting/nodes/preprocess/node.py`, `extract_participants/node.py`, `identify_topics/node.py`, `extract_actions/node.py`, `generate_minutes/node.py`, `create_summary/node.py`, `mock_result/node.py` (y cualquier otro bajo `src/agents/meeting/nodes/` que referencie el campo)
- [x] T006 In `src/agents/meeting/nodes/preprocess/node.py`, si `len(raw.split()) < get_meeting_min_words()` tras strip, append advertencia en español según spec (coherente con constitución IV y FR-014)
- [x] T007 Extend `ProcessMeetingResponse` in `src/api/routers/process.py` with `status`, `processing_errors: list[str]`, `transcript: str` (default vacío); implement helper mapping `dict` post-`invoke` → response; usar en **POST** síncronos `/text` y rutas de archivo que devuelvan JSON único
- [x] T008 Change `MeetingRecordResponse.processing_errors` to `list[str]` in `src/api/routers/meetings.py` y poblar con `decode_processing_errors` desde columna `Text` al validar filas ORM
- [x] T009 Align evento terminal de éxito en `src/api/process_file_stream.py` (`type` de resultado final) con `specs/013-incomplete-error-feedback/contracts/processing-feedback.md`: mismos campos lógicos que T007 (`status`, lista `processing_errors`, `transcript` si existe)

**Checkpoint**: `curl`/Swagger muestra `processing_errors` como **array** y `status` en 200; SSE entrega payload equivalente; persistencia guarda JSON en columna sin romper lectura de filas antiguas (decode tolerante)

---

## Phase 3: User Story 1 — Entender qué ocurrió sin jerga técnica (Priority: P1) 🎯 MVP core backend

**Goal**: Mensajes español, sin stacks en JSON, fallos de transcripción/modelo mapeados a estado y avisos (FR-003, FR-009, FR-013, spec US1)

**Independent Test**: Forzar transcripción fallida y timeout; respuestas HTTP/SSE sin substring `Traceback`; `status` `failed`/`partial` coherente; logs del servidor contienen detalle técnico

### Implementation for User Story 1

- [x] T010 [US1] Register FastAPI exception handlers in `src/api/main.py` for excepciones no previstas: `detail` genérico en **español**, log con stack solo en servidor (no en cuerpo JSON)
- [x] T011 [US1] Audit `src/services/transcription.py` y rutas en `src/api/routers/process.py` / `src/api/process_file_stream.py` para que mensajes hacia cliente (state, `HTTPException`, SSE `detail`) sean español; reservar trazas a `logger`
- [x] T012 [P] [US1] Add `tests/unit/db/test_processing_errors_codec.py` (round-trip JSON, legacy plain string → lista de un elemento o regla documentada en codec)
- [x] T013 [P] [US1] Add `tests/unit/agents/meeting/test_preprocess_min_words.py` (umbral desde config mock/stub)

**Checkpoint**: Criterios de quickstart API para errores “humanos” y forma de lista

---

## Phase 4: User Story 2 — Validar la entrada antes de procesar (Priority: P1)

**Goal**: Validación vacía/archivo inválido con mensaje claro en el flujo de acción (spec US2, FR-006)

**Independent Test**: UI: pulsar procesar sin datos; API: 422/400 con `detail` comprensible en español

### Implementation for User Story 2

- [x] T014 [US2] In `src/ui/app.py`, mostrar retroalimentación de validación (texto/archivo faltante, archivo no válido) **junto al flujo** del botón procesar, en español, sin depender solo de excepciones genéricas
- [x] T015 [P] [US2] Revisar cadenas `detail` en `src/services/file_loader.py` y rechazos en `src/api/routers/process.py` para tono y claridad en español alineados a FR-006

---

## Phase 5: User Story 3 — Separar avisos del análisis y detalles técnicos (Priority: P2)

**Goal**: Bloque “Avisos” dedicado con scroll, estado visible como **texto**, acordeón colapsado para metadatos seguros (spec US3, FR-004, FR-005, FR-007, FR-010, FR-011)

**Independent Test**: Resultado con lista larga de avisos: todos visibles con scroll; estado legible sin color; acordeón técnico cerrado al inicio y sin secretos

### Implementation for User Story 3

- [x] T016 [US3] Refactor `src/ui/app.py` para renderizar **avisos** (`processing_errors`) en panel/HTML dedicado separado del Markdown de análisis; badge o etiqueta textual para `completed`/`partial`/`failed`; área de avisos con **scroll** si la lista es larga
- [x] T017 [P] [US3] Add `gr.Accordion` “Detalles técnicos” (cerrado por defecto) in `src/ui/app.py` con metadatos seguros: p. ej. backend de transcripción (`get_transcription_backend()`), hint de timeout desde `src/config.py` — **prohibido** mostrar API keys, `DATABASE_URL` completo o rutas internas
- [x] T018 [P] [US3] Ajustar estilos en `src/ui/status_loader.py` y/o crear `src/ui/theme.py` para tokens CSS alineados al tema Gradio (callouts accesibles claro/oscuro) según plan

---

## Phase 6: User Story 4 — Copiar transcripción final (Priority: P2)

**Goal**: Exponer `transcript` en estado/API/SSE y UI con acción copiar (spec US4, FR-008)

**Independent Test**: Flujo multimedia exitoso: campo transcripción visible, botón copiar, pegado contiene texto íntegro; sin transcripción: control oculto o vacío no confundido con resumen

### Implementation for User Story 4

- [x] T019 [US4] Asegurar que el texto transcrito final se escribe en `MeetingState` (`transcript`) durante el flujo multimedia en puntos adecuados (`src/api/process_file_stream.py` y/o nodos/servicios que produzcan STT) y se propaga al evento final T009 / respuesta T007
- [x] T020 [US4] In `src/ui/app.py`, añadir componente de solo lectura etiquetado “Transcripción” con acción **Copiar** (API Gradio según versión, p. ej. `Textbox` con `buttons`) cuando `transcript` no vacío; ocultar o vaciar coherentemente si no hubo STT

---

## Phase 7: User Story 5 — Misma lógica en historial (Priority: P3)

**Goal**: Reutilizar patrón avisos + estado + secciones cuando exista vista de historial (spec US5, FR-012)

**Independent Test**: Abrir detalle `partial`/`failed` desde historial (si la UI ya lo tiene) y comparar con pantalla principal

### Implementation for User Story 5

- [x] T021 [US5] Extraer función o módulo reutilizable (p. ej. `src/ui/result_layout.py` o helpers en `src/ui/app.py`) que dado `status`, `processing_errors`, campos de análisis y `transcript` genere el mismo layout que el flujo principal; invocarlo desde el callback de historial/detalle **si** existe en `src/ui/app.py`; si el historial aún no está implementado, dejar integración documentada en comentario `TODO(US-009)` mínimo sin romper build

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Contrato HTTP, regresiones de tests existentes, calidad

- [x] T022 [P] Add `tests/integration/api/test_process_feedback_shape.py`: `POST /api/v1/process/text` con texto corto → `status` y `processing_errors` lista; aserción de que `detail` de error no contiene `Traceback` en casos provocados
- [x] T023 [P] Update `tests/unit/db/test_meeting_repository.py` (y cualquier test que asuma `processing_errors` string en API) para persistencia JSON y respuestas `list[str]`
- [x] T024 Run `pytest` desde la raíz del repo sobre `tests/` y `ruff check src`; corregir fallos introducidos por esta feature
- [x] T025 [P] Añadir referencia breve al contrato `specs/013-incomplete-error-feedback/contracts/processing-feedback.md` en docstrings o descripciones OpenAPI de `src/api/routers/process.py` / `meetings.py` si aplica
- [ ] T026 Walkthrough manual siguiendo `specs/013-incomplete-error-feedback/quickstart.md` y anotar brechas en código o en el propio quickstart

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4–7 (US2–US5) → Phase 8
```

- **US2** puede empezar tras T007–T009 si solo valida API, pero **T014** necesita respuesta con lista desde backend → idealmente Phase 2 completa.
- **US3–US4** dependen de Phase 2 + eventos SSE/API actualizados (T009, T007).
- **US5** depende de **US3** (mismo layout) y de existencia de UI de historial (puede quedar preparador sin UI).

### User Story Dependencies

| Story | Depende de |
|-------|------------|
| US1 | Phase 2 |
| US2 | Phase 2 (respuesta estable); mejora con US1 para tono de error |
| US3 | Phase 2 + datos reales de lista en cliente |
| US4 | Phase 2 + T019 datos `transcript` |
| US5 | US3 layout + hook historial |

### Parallel Opportunities

- T012 y T013 en Phase 3 (tests distintos) tras T003–T006
- T015 en paralelo con T014 si no comparten mismas líneas sin merge
- T017 y T018 en paralelo con cuidado (ambos UI — preferir secuencia si un solo PR)
- T022 y T023 en Phase 8 en paralelo
- T025 en paralelo con T024 si no toca mismos archivos que ruff corrige

---

## Parallel Example: Phase 3 (US1)

```bash
# Tras completar Phase 2:
# Terminal A: implementar T012 tests/unit/db/test_processing_errors_codec.py
# Terminal B: implementar T013 tests/unit/agents/meeting/test_preprocess_min_words.py
# T010–T011 secuenciales en main.py / servicios
```

---

## Parallel Example: Phase 8

```bash
# T022 tests/integration/api/test_process_feedback_shape.py
# T023 tests/unit/db/test_meeting_repository.py
```

---

## Implementation Strategy

### MVP First (backend visible)

1. Phase 1 + Phase 2 (T001–T009)  
2. Phase 3 US1 (T010–T013)  
3. Demostrar con Swagger/curl + quickstart API

### Incremental Delivery

1. MVP backend anterior  
2. US2 validación UI/API  
3. US3 presentación (bloque avisos + tema)  
4. US4 transcripción copiable  
5. US5 historial cuando exista sidebar/listado  
6. Polish: T022–T026

### Suggested MVP Scope

- **Mínimo entregable spec 013 en API**: T001–T013 + T022 (integración básica)  
- **Producto alineado a US-011 en pantalla**: hasta T020 + T026 manual  

---

## Notes

- Los IDs van de **T001** a **T026**; no reutilizar números al añadir tareas (continuar T027+).  
- Cualquier cambio de esquema de columna distinto a `Text` + JSON queda **fuera** del MVP salvo decisión explícita en implementación (ver research.md).  
- Mantener **Principio I**: la UI no implementa umbral de 20 palabras ni lógica de negocio de errores — solo presentación y validación vacía local opcional (T014).
