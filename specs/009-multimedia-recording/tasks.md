# Tasks: Procesar grabación multimedia

**Input**: Design documents from `/specs/009-multimedia-recording/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios e integración).

**Organization**: Tareas agrupadas por user story; US1 (audio) y US2 (video) comparten transcripción; US3 validación rechazo.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura existente de MeetMind

---

## Phase 1: Setup

**Purpose**: Dependencias y estructura para transcripción y tests

- [x] T001 Add `openai-whisper` to `pyproject.toml` dependencies
- [x] T002 Ensure `tests/unit/services/` and `tests/unit/api/` and `tests/integration/api/` directories exist

---

## Phase 2: Foundational (Bloqueante)

**Purpose**: Configuración, servicio de transcripción y validación multimedia — BLOQUEA todas las user stories

**⚠️ CRITICAL**: Sin esto no se puede implementar US1/US2

- [x] T003 Add `get_transcription_model()`, `get_max_file_size_mb()`, `get_processing_timeout_sec()` to `src/config.py` (defaults: small, 500, 900; ver `get_transcription_language`, `get_whisper_device`)
- [x] T004 Create `src/services/transcription.py` with `TranscriptionError` exception and `transcribe_audio(audio_path, model=..., language=...) -> str`; handle video (extract audio with ffmpeg to temp WAV) per contracts/transcription-service.md
- [x] T005 [P] Add constants `MULTIMEDIA_EXTENSIONS`, `MULTIMEDIA_MIME_TYPES`, `MAX_MULTIMEDIA_BYTES` in `src/api/routers/process.py` or shared module; function `validate_multimedia_file(extension, content_type, size_bytes) -> str | None` (returns error message or None)
- [x] T006 [P] Unit test for `transcribe_audio` with mocked Whisper in `tests/unit/services/test_transcription.py` (mock whisper.load_model and transcribe; verify TranscriptionError on failure)

**Checkpoint**: Config, transcripción y validación listos; tests pasan

---

## Phase 3: User Story 1 - Subir archivo de audio (Priority: P1) 🎯 MVP

**Goal**: Aceptar MP3, WAV, M4A; transcribir; ejecutar workflow; devolver participantes, temas, acciones, minuta, resumen

**Independent Test**: Subir MP3 válido → transcripción → resultados estructurados; feedback durante procesamiento (API responde cuando termina)

### Implementation for User Story 1

- [x] T007 [US1] Extend `process_file` in `src/api/routers/process.py`: add `.mp3`, `.wav`, `.m4a` to allowed extensions; if extension in multimedia, validate (size ≤ 500 MB), write to temp file, call `transcribe_audio`, then `graph.invoke({"raw_text": text})`
- [x] T008 [US1] Keep existing text flow (`.txt`, `.md`) in `process_file`; route by extension: multimedia → transcribe; text → `load_text_file`
- [x] T009 [US1] Wrap transcription + graph in timeout (15 min); on timeout raise HTTP 408 with message "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde." per contracts/api-process-multimedia.md
- [x] T010 [US1] On `TranscriptionError` raise HTTP 422 with detail "El formato del archivo no es compatible." or "No se pudo procesar el archivo." (no stack trace)

**Checkpoint**: MP3/WAV/M4A → transcripción → workflow → respuesta 200; timeout y errores con mensajes en español

---

## Phase 4: User Story 2 - Subir archivo de video (Priority: P1)

**Goal**: Aceptar MP4, MOV, WEBM, MKV; extraer audio, transcribir, workflow; mismos resultados

**Independent Test**: Subir MP4 válido → extracción de audio → transcripción → resultados

### Implementation for User Story 2

- [x] T011 [US2] Add `.mp4`, `.mov`, `.webm`, `.mkv` to allowed extensions in `process_file` in `src/api/routers/process.py`; same transcribe path (transcription.py already extracts audio for video)
- [x] T012 [P] [US2] Integration test: `POST /api/v1/process/file` with MP4 fixture in `tests/integration/api/test_process_file_multimedia.py` (or skip if no fixture; document in quickstart)

**Checkpoint**: MP4/MOV/WEBM/MKV → mismos resultados que audio

---

## Phase 5: User Story 3 - Rechazo de formatos no soportados (Priority: P2)

**Goal**: Extensiones no permitidas (.avi, .exe) → 415 con mensaje claro "Formato no soportado. Formatos permitidos: MP4, MOV, MP3, WAV, M4A, WEBM, MKV."

**Independent Test**: Subir .avi → 415; mensaje indica formatos permitidos

### Implementation for User Story 3

- [x] T013 [US3] Ensure `process_file` rejects extensions not in (multimedia + text) with HTTP 415 and detail "Formato no soportado. Formatos permitidos: MP4, MOV, MP3, WAV, M4A, WEBM, MKV." per contracts/multimedia-validation.md
- [x] T014 [US3] Ensure file size > 500 MB returns HTTP 400 "El archivo supera el límite de 500 MB." for multimedia files
- [x] T015 [P] [US3] Unit test: invalid extension (.avi) and oversize file → 415 and 400 in `tests/unit/api/test_process_multimedia.py`

**Checkpoint**: Formato inválido o > 500 MB → mensaje amigable en español

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Tests adicionales, quickstart, alineación con 008

- [x] T016 [P] Add unit test: valid MP3 path through transcription (mock) in `tests/unit/services/test_transcription.py`
- [x] T017 Update `specs/009-multimedia-recording/quickstart.md` with verified curl examples; add note about ffmpeg prerequisite
- [x] T018 Consider aligning UI timeout (008) with API 15 min when 009 is active; document in quickstart or plan
- [ ] T019 Run quickstart validation per `specs/009-multimedia-recording/quickstart.md` (MP3, MP4, .avi, > 500 MB)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Sin dependencias
- **Phase 2 (Foundational)**: Tras Setup — BLOQUEA US1, US2, US3
- **Phase 3 (US1)**: Tras Foundational — Flujo principal audio
- **Phase 4 (US2)**: Tras US1 — Añadir video (mismo código, más extensiones)
- **Phase 5 (US3)**: Tras Foundational — Validación rechazo
- **Phase 6 (Polish)**: Tras fases 3–5

### User Story Dependencies

- **US1 (P1)**: Tras Foundational
- **US2 (P1)**: Tras US1 (comparte transcripción; añade extensiones video)
- **US3 (P2)**: Tras Foundational (validación); puede implementarse en paralelo con US1 si hay capacidad

### Parallel Opportunities

- T005, T006: validación y test transcripción en paralelo
- T012, T015, T016: tests en paralelo

---

## Parallel Example: Phase 2

```bash
# Tras T003, T004:
Task T005: "Add validation constants and validate_multimedia_file"
Task T006: "Unit test for transcribe_audio with mocked Whisper"
```

---

## Implementation Strategy

### MVP First (US1)

1. Phase 1: Setup
2. Phase 2: Foundational (config, transcription, validation)
3. Phase 3: US1 (audio en process_file)
4. **STOP and VALIDATE**: curl con MP3 → resultados
5. Demo listo

### Incremental Delivery

1. Setup + Foundational → Transcripción y validación listas
2. US1 → Audio (MP3, WAV, M4A)
3. US2 → Video (MP4, MOV, WEBM, MKV)
4. US3 → Rechazo claro de formatos inválidos
5. Polish → Tests + quickstart

---

## Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001, T002 | 2 |
| 2. Foundational | T003–T006 | 4 |
| 3. US1 (MVP) | T007–T010 | 4 |
| 4. US2 | T011, T012 | 2 |
| 5. US3 | T013–T015 | 3 |
| 6. Polish | T016–T019 | 4 |
| **Total** | | **19** |

**MVP scope**: Phases 1–3 (T001–T010) — 10 tasks

---

## Requisitos diferidos (iteración futura)

| Requisito | Alcance diferido | Cubierto en MVP por |
|-----------|------------------|---------------------|
| FR-007 (flujo async tras timeout) | Job en background, usuario consulta resultado más tarde | T009: HTTP 408 con mensaje amigable |
| FR-010 (job ID, GET /jobs/{id}) | Almacén de jobs, endpoint de consulta | — |
