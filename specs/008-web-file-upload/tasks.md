# Tasks: Subir archivos desde la interfaz web

**Input**: Design documents from `/specs/008-web-file-upload/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para validación de archivos).

**Organization**: Tareas agrupadas por user story; US1 y US2 comparten validación; US3 errores; US4 ya cubierto por config.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3, US4)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura existente de MeetMind

---

## Phase 1: Setup

**Purpose**: Estructura para módulo de validación y tests

- [x] T001 Ensure `tests/unit/ui/` directory exists (create if missing)

---

## Phase 2: Foundational (Módulo de validación)

**Purpose**: Crear módulo de validación reutilizable que bloquea todas las user stories

**⚠️ CRITICAL**: Sin validación, no se puede implementar US1/US2 correctamente

- [x] T002 Create `src/ui/utils.py` with `ALLOWED_EXTENSIONS` (`.mp4`, `.mov`, `.mp3`, `.wav`, `.m4a`, `.txt`, `.md`), `MAX_FILE_SIZE_BYTES` (500 * 1024 * 1024), `validate_file_extension(path) -> str | None`, `validate_file_size(path) -> str | None`, `validate_file(path) -> str | None` (returns error message or None if valid)
- [x] T003 [P] Unit tests for `validate_file_extension`, `validate_file_size`, `validate_file` in `tests/unit/ui/test_validation.py` per contracts/file-validation.md

**Checkpoint**: Módulo de validación listo; tests pasan

---

## Phase 3: User Story 1 - Cargar archivo válido y ver resultados (Priority: P1) 🎯 MVP

**Goal**: Aceptar archivos multimedia y texto, enviar a la API, mostrar resultados en secciones; feedback visual durante procesamiento

**Independent Test**: Subir archivo TXT o MP3 válido → feedback visual → resultados en secciones (participantes, temas, acciones, minuta, resumen)

### Implementation for User Story 1

- [x] T004 [US1] Update `gr.File` in `src/ui/app.py`: `file_types=[".txt", ".md", ".mp4", ".mov", ".mp3", ".wav", ".m4a"]`, label "O sube un archivo (TXT, MD, MP4, MOV, MP3, WAV, M4A)"
- [x] T005 [US1] Update `process_meeting_file` in `src/ui/app.py`: call `validate_file(path)` before sending; if error, return message and do not send
- [x] T006 [US1] Update `process_meeting_file` in `src/ui/app.py`: `httpx.Client(timeout=600.0)` (10 min) for file processing
- [x] T007 [US1] Add `get_mime_for_extension(filename)` in `src/ui/utils.py` and use in `process_meeting_file` when building `files` dict for multipart (support text/plain, text/markdown, video/mp4, video/quicktime, audio/mpeg, audio/wav, audio/mp4)

**Checkpoint**: Archivo válido (TXT/MD/MP3/etc.) → validación OK → envío con timeout 10 min → resultados formateados; archivo inválido → mensaje antes de enviar

---

## Phase 4: User Story 2 - Validación de tipos de archivo (Priority: P1)

**Goal**: Rechazar formatos no soportados y archivos >500 MB antes de enviar; mensaje claro con formatos permitidos

**Independent Test**: Archivo .exe o .zip o >500 MB → mensaje de error claro; no se envía a la API

### Implementation for User Story 2

- [x] T008 [US2] Ensure validation error messages in `src/ui/utils.py` match `specs/008-web-file-upload/contracts/file-validation.md`: "Formato no soportado. Formatos permitidos: multimedia (MP4, MOV, MP3, WAV, M4A), texto (TXT, MD)." and "El archivo supera el límite de 500 MB."
- [x] T009 [P] [US2] Unit test: invalid extension (.exe) and oversize file → `validate_file` returns correct Spanish messages in `tests/unit/ui/test_validation.py`

**Checkpoint**: Formato inválido o tamaño excedido → mensaje amigable en español; no envío

---

## Phase 5: User Story 3 - Errores de procesamiento amigables (Priority: P2)

**Goal**: Timeout, conexión, HTTP 4xx/5xx → mensaje amigable en español; nunca stack traces ni códigos HTTP crudos

**Independent Test**: Simular timeout o error HTTP → mensaje comprensible para el usuario

### Implementation for User Story 3

- [x] T010 [US3] Update `process_meeting_file` and `process_meeting_text` in `src/ui/app.py`: catch `httpx.TimeoutException` → return "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto."
- [x] T011 [US3] Update HTTP error handling in both process functions: extract `detail` from `response.json()` if possible; present user-friendly message; never expose status code, stack trace, or raw response to user
- [x] T012 [US3] Ensure `httpx.ConnectError` and generic `Exception` return Spanish messages per data-model.md (connection: "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada.")

**Checkpoint**: Errores de API → mensajes amigables en español; sin detalles técnicos

---

## Phase 6: User Story 4 - Configuración URL (Priority: P3)

**Goal**: URL configurable vía variable de entorno; documentada en quickstart

**Independent Test**: `API_BASE_URL` distinta → UI consume ese endpoint

### Implementation for User Story 4

- [x] T013 [US4] Verify `src/ui/app.py` uses `get_api_base_url()` from `src/config.py` for both `process_meeting_file` and `process_meeting_text`; document `API_BASE_URL` in `specs/008-web-file-upload/quickstart.md` if not already present

**Checkpoint**: URL configurable; documentada

---

## Phase 7: Polish & Cross-Cutting

**Purpose**: Validación final, tests adicionales, quickstart

- [x] T014 [P] Add unit test: valid extensions and size → `validate_file` returns None in `tests/unit/ui/test_validation.py`
- [ ] T015 Run quickstart validation per `specs/008-web-file-upload/quickstart.md` (archivo válido, inválido, >500 MB, timeout si posible)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias
- **Foundational (Phase 2)**: Tras Setup — BLOQUEA US1, US2
- **Phase 3 (US1)**: Tras Foundational — Flujo principal
- **Phase 4 (US2)**: Tras Foundational; mensajes ya integrados en T005; T008 refina
- **Phase 5 (US3)**: Tras US1 — Errores en process functions
- **Phase 6 (US4)**: Verificación y documentación
- **Polish (Phase 7)**: Tras fases 3–6

### User Story Dependencies

- **US1 (P1)**: Tras Foundational
- **US2 (P1)**: Tras Foundational (validación); se integra con US1 en T005
- **US3 (P2)**: Tras US1 (modifica process functions)
- **US4 (P3)**: Independiente; verificación

### Parallel Opportunities

- T003, T009, T014: tests en paralelo
- T008 puede hacerse en paralelo con T007 si hay dos desarrolladores

---

## Parallel Example: Phase 2

```bash
# Tras T002:
Task T003: "Unit tests for validation in tests/unit/ui/test_validation.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Phase 1: Setup
2. Phase 2: Foundational (validación)
3. Phase 3: US1 (upload, timeout, validación integrada)
4. Phase 4: US2 (mensajes de error de validación)
5. **STOP and VALIDATE**: Subir TXT válido → resultados; subir .exe → mensaje
6. Demo listo

### Incremental Delivery

1. Setup + Foundational → Validación lista
2. US1 → Flujo principal con archivos válidos
3. US2 → Mensajes para archivos inválidos
4. US3 → Errores de API amigables
5. US4 → Verificación URL
6. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. US1 (MVP) | T004–T007 | 4 |
| 4. US2 | T008, T009 | 2 |
| 5. US3 | T010–T012 | 3 |
| 6. US4 | T013 | 1 |
| 7. Polish | T014, T015 | 2 |
| **Total** | | **15** |

**MVP scope**: Phases 1–4 (T001–T009) — 9 tasks
