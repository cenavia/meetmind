# Tasks: Procesar notas en texto

**Input**: Design documents from `/specs/002-text-notes-processing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para file_loader e integración para endpoint file).

**Organization**: Tareas agrupadas por user story para implementación y validación independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001-hello-world-e2e

---

## Phase 1: Setup (Estructura compartida)

**Purpose**: Inicializar la estructura necesaria para la feature (extensión de 001)

- [x] T001 Create `src/services/` directory and `src/services/__init__.py`

---

## Phase 2: Foundational (Prerrequisitos bloqueantes)

**Purpose**: Servicio file_loader que DEBE existir antes de cualquier user story

**⚠️ CRITICAL**: Ningún trabajo de user story puede comenzar hasta completar esta fase

- [x] T002 Implement `load_text_file()` in `src/services/file_loader.py` with UTF-8 default, latin-1 fallback, extension validation (.txt, .md), max 50.000 characters
- [x] T003 [P] Unit tests for file_loader in `tests/unit/services/test_file_loader.py` (empty file, encoding UTF-8/latin-1, length limit, invalid extension)

**Checkpoint**: file_loader operativo — puede comenzar implementación de user stories

---

## Phase 3: User Story 1 - Subir archivo TXT (Priority: P1) 🎯 MVP

**Goal**: Usuario puede subir archivo .txt y recibir documentación estructurada; barra de progreso y "Procesando..."; sin transcripción

**Independent Test**: Subir .txt con notas → ver 5 salidas estructuradas; no se ejecuta STT

### Implementation for User Story 1

- [x] T004 [US1] Add `POST /api/v1/process/file` endpoint in `src/api/routers/process.py` (UploadFile, validation: extension, MIME, empty, length; use file_loader; invoke graph)
- [x] T005 [US1] Integration test for `/process/file` in `tests/integration/test_api_process_file.py` (200, 400, 422, 415 según contract)
- [x] T006 [US1] Add `gr.File` with `file_types=[".txt", ".md"]` and mutual lock (disable text when file selected, disable file when text has content) in `src/ui/app.py`
- [x] T007 [US1] Add progress bar during upload and "Procesando..." during analysis in file upload handler in `src/ui/app.py`; call API with file via httpx multipart

**Checkpoint**: User Story 1 funcional — subir .txt → resultado estructurado; UI con bloqueo y feedback

---

## Phase 4: User Story 2 - Subir archivo Markdown (Priority: P2)

**Goal**: Usuario puede subir archivo .md y recibir la misma documentación estructurada

**Independent Test**: Subir .md con notas → ver 5 salidas estructuradas

### Implementation for User Story 2

- [x] T008 [P] [US2] Add integration test for .md file in `tests/integration/test_api_process_file.py`
- [x] T009 [US2] Confirm in T004/T006 that API validates `text/markdown` and UI `file_types` includes `.md`; add integration test for .md MIME if missing in tests/integration/test_api_process_file.py

**Checkpoint**: User Stories 1 y 2 funcionales — .txt y .md ambos soportados

---

## Phase 5: User Story 3 - Preservar encoding (Priority: P3)

**Goal**: Caracteres especiales (ñ, á, é) se interpretan correctamente; fallback latin-1 cuando UTF-8 falla

**Independent Test**: Subir archivo con ñ, á, é → salida conserva caracteres; archivo latin-1 → se procesa o mensaje claro

### Implementation for User Story 3

- [x] T010 [P] [US3] Add unit tests for encoding (UTF-8 with special chars, latin-1 fallback, both fail) in `tests/unit/services/test_file_loader.py`
- [x] T011 [P] [US3] Add integration test with special characters (ñ, á, é) in `tests/integration/test_api_process_file.py`

**Checkpoint**: Encoding correctamente manejado en toda la cadena

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentación y validación final

- [x] T012 [P] Update `docs/planning/COMO-EJECUTAR.md` with file upload flow (archivos TXT/MD)
- [x] T013 Run quickstart validation per `specs/002-text-notes-processing/quickstart.md` (incl. verificación manual de que archivo típico <5k chars procesa en <30s — SC-001)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las user stories
- **User Stories (Phase 3–5)**: Dependen de Foundational
  - US1 → US2 (US2 valida .md; depende de endpoint de US1)
  - US3 (encoding) implementado en file_loader (Phase 2); Phase 5 añade tests
- **Polish (Phase 6)**: Depende de US1–US3 completas

### User Story Dependencies

- **US1 (P1)**: Tras Phase 2 — Sin dependencias de otras stories
- **US2 (P2)**: Tras US1 — Mismo endpoint; validación adicional
- **US3 (P3)**: Implementación en Phase 2 (file_loader); Phase 5 = tests

### Parallel Opportunities

- T003 puede ejecutarse en paralelo con T002 (tests una vez file_loader tiene interfaz definida)
- T010, T011 pueden ejecutarse en paralelo
- T012 puede ejecutarse en paralelo con otras tareas de Polish

---

## Parallel Example: Phase 2

```bash
# Tras definir la interfaz de file_loader:
Task T002: "Implement load_text_file in src/services/file_loader.py"
# Luego en paralelo:
Task T003: "Unit tests in tests/unit/services/test_file_loader.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Setup
2. Phase 2: Foundational (file_loader + tests)
3. Phase 3: US1 (API endpoint + UI)
4. **STOP and VALIDATE**: Probar subida de .txt → resultado estructurado
5. Demo listo

### Incremental Delivery

1. Setup + Foundational → file_loader operativo
2. US1 → Subir .txt → Demo (MVP)
3. US2 → Validar .md → Demo
4. US3 → Validar encoding → Demo
5. Polish → Documentación actualizada

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. US1 (MVP) | T004–T007 | 4 |
| 4. US2 | T008, T009 | 2 |
| 5. US3 | T010, T011 | 2 |
| 6. Polish | T012, T013 | 2 |
| **Total** | | **13** |

**MVP scope**: Phases 1–3 (T001–T007) — 7 tasks
