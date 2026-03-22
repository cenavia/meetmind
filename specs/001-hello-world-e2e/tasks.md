# Tasks: Estructura inicial y Hello World E2E

**Input**: Design documents from `/specs/001-hello-world-e2e/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks — spec requiere verificación manual (SC-004). Tests opcionales según plan.

**Organization**: Tasks agrupados por user story para implementación y validación independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story asociada (US1, US2, US3)
- Incluir rutas exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en raíz del repositorio
- Convenciones de plan.md: `src/api/`, `src/agents/meeting/`, `src/ui/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto y estructura base

- [x] T001 Create directory structure per plan.md: `src/api/`, `src/api/routers/`, `src/agents/meeting/nodes/preprocess/`, `src/agents/meeting/nodes/mock_result/`, `src/ui/`, `tests/unit/agents/meeting/`, `tests/integration/`
- [x] T002 Create `pyproject.toml` with uv, Python 3.11+, dependencies: fastapi, uvicorn, gradio, langgraph, langchain-core, httpx, pydantic
- [x] T003 [P] Create `.env.example` with `API_BASE_URL=http://localhost:8000`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura base que DEBE estar lista antes de cualquier user story

**⚠️ CRITICAL**: Ningún trabajo de user story puede empezar hasta completar esta fase

- [x] T004 Create `src/config.py` with Settings (API_BASE_URL from env, default `http://localhost:8000`)
- [x] T005 [P] Create `__init__.py` in `src/`, `src/api/`, `src/api/routers/`, `src/agents/`, `src/agents/meeting/`, `src/agents/meeting/nodes/`, `src/agents/meeting/nodes/preprocess/`, `src/agents/meeting/nodes/mock_result/`, `src/ui/`, `tests/`, `tests/unit/`, `tests/unit/agents/`, `tests/unit/agents/meeting/`, `tests/integration/`

**Checkpoint**: Base lista — se puede iniciar implementación de user stories

---

## Phase 3: User Story 1 — Verificar que el servicio API está operativo (Priority: P1) 🎯 MVP

**Goal**: Endpoint GET /health que responda 200 e indique operatividad del servicio

**Independent Test**: `curl http://localhost:8000/health` → 200 y cuerpo con status "ok"

### Implementation for User Story 1

- [x] T006 [US1] Create `src/api/main.py` with FastAPI app, CORS básico
- [x] T007 [US1] Create `src/api/routers/health.py` with GET /health returning `{"status": "ok"}`
- [x] T008 [US1] Create `src/api/dependencies.py` (placeholder; get_graph se añade en US2)
- [x] T009 [US1] Mount health router at / in `src/api/main.py`; add uvicorn run instructions in docstring or README

**Checkpoint**: API responde en /health — validar con curl antes de continuar

---

## Phase 4: User Story 2 — Procesar texto vía API (Priority: P2)

**Goal**: POST /api/v1/process/text que acepte JSON con text, invoque el grafo LangGraph y devuelva participantes, topics, actions, minutes, executive_summary

**Independent Test**: `curl -X POST http://localhost:8000/api/v1/process/text -H "Content-Type: application/json" -d '{"text": "Reunión con Juan y María."}'` → 200 y JSON con los 5 campos

### Implementation for User Story 2

- [x] T010 [US2] Create `src/agents/meeting/state.py` with MeetingState TypedDict (raw_text, participants, topics, actions, minutes, executive_summary)
- [x] T011 [US2] Create `src/agents/meeting/nodes/preprocess/node.py` — normaliza raw_text (strip, mínima transformación)
- [x] T012 [US2] Create `src/agents/meeting/nodes/mock_result/node.py` — retorna datos hardcodeados según data-model.md
- [x] T013 [US2] Create `src/agents/meeting/agent.py` with `get_graph()`: StateGraph preprocess → mock_result → END
- [x] T014 [US2] Create `src/api/routers/process.py` with POST /api/v1/process/text: Pydantic request (text, max 50_000 chars), validation, invoke graph, return response
- [x] T015 [US2] Add ProcessTextRequest and ProcessMeetingResponse models in `src/api/routers/process.py` (or `src/api/models.py`); reject with 400 if text > 50_000
- [x] T016 [US2] Update `src/api/dependencies.py` with `get_graph` Depends
- [x] T017 [US2] Mount process router at /api/v1 in `src/api/main.py`

**Checkpoint**: POST /api/v1/process/text devuelve JSON estructurado — validar con curl

---

## Phase 5: User Story 3 — Flujo completo desde Gradio (Priority: P3)

**Goal**: UI Gradio con input, botón Procesar, llamada a API vía HTTP, estado de carga, validación texto vacío, manejo de error si API no disponible

**Independent Test**: Ejecutar API + Gradio, escribir texto, pulsar Procesar → ver resultado estructurado; vacío → botón deshabilitado o mensaje; API caída → mensaje de error

### Implementation for User Story 3

- [x] T018 [US3] Create `src/ui/app.py` with Gradio Blocks, gr.Textbox (input), gr.Button ("Procesar"), gr.Markdown or gr.Textbox (output)
- [x] T019 [US3] Implement `process_meeting(text)` in `src/ui/app.py` that calls POST {API_BASE_URL}/api/v1/process/text via httpx
- [x] T020 [US3] Add loading state in Gradio: show "Procesando..." or disable button during request (FR-009)
- [x] T021 [US3] Add validation: disable "Procesar" button when input is empty or only whitespace (FR-004)
- [x] T022 [US3] Add error handling: when API unavailable (ConnectionError, timeout), show user-friendly message in output (no silent failure)

**Checkpoint**: Flujo E2E completo — texto → Procesar → resultado; vacío bloqueado; error API mostrado

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentación y validación final

- [x] T023 [P] Update `docs/planning/COMO-EJECUTAR.md` per quickstart.md: uv sync, comandos API/UI, API_BASE_URL, flujo E2E (FR-006)
- [x] T024 Run quickstart validation: seguir COMO-EJECUTAR.md y verificar SC-001 (flujo completo <15 min)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA todas las user stories
- **User Stories (Phase 3–5)**: Dependen de Foundational
  - US1 (Phase 3): Independiente
  - US2 (Phase 4): Independiente de US1 (pero montaje en main.py requiere estructura US1)
  - US3 (Phase 5): Requiere API funcionando (US1 + US2)
- **Polish (Phase 6)**: Depende de US1, US2, US3 completas

### User Story Dependencies

- **US1 (P1)**: Tras Foundational — base para API
- **US2 (P2)**: Tras Foundational — añade process/text; US3 necesita ambos
- **US3 (P3)**: Tras US1+US2 — UI invoca API

### Parallel Opportunities

- T003, T005: paralelizables dentro de su fase
- T010, T011, T012: modelos/nodos en US2 pueden hacerse en paralelo
- T023: documentación en paralelo con validación manual

---

## Parallel Example: User Story 2

```bash
# Nodos en paralelo:
T011: preprocess/node.py
T012: mock_result/node.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational
3. Completar Phase 3: User Story 1
4. **STOP y VALIDAR**: `curl http://localhost:8000/health`
5. Demo si aplica

### Incremental Delivery

1. Setup + Foundational → base lista
2. US1 → health check → Demo (API operativa)
3. US2 → process/text → Demo (API completa)
4. US3 → Gradio E2E → Demo (flujo completo)
5. Polish → COMO-EJECUTAR.md actualizado → Validación SC-001

---

## Notes

- [P] = archivos distintos, sin dependencias cruzadas
- [Story] = trazabilidad a user story
- Cada user story debe poder completarse y probarse de forma independiente
- Commit tras cada tarea o grupo lógico
- Parar en cada checkpoint para validar
- Evitar: tareas vagas, conflictos en el mismo archivo, dependencias cruzadas que rompan independencia
