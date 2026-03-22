# Tasks: Ver minuta formal

**Input**: Design documents from `/specs/006-generate-minutes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para generate_minutes, integración para flujo completo).

**Organization**: Tareas agrupadas por user story; US1–US3 se implementan incrementalmente en el mismo nodo generate_minutes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001-005

---

## Phase 1: Setup (Estructura del nodo)

**Purpose**: Crear la estructura del nodo generate_minutes según Principio II (nodos autocontenidos)

- [x] T001 Create `src/agents/meeting/nodes/generate_minutes/` directory with `__init__.py`, `node.py` (stub returning `{"minutes": "Minuta: No se identificó información procesable en la reunión."}`), `prompt.py` (stub)

---

## Phase 2: Foundational (Integración en el grafo)

**Purpose**: Integrar generate_minutes en el grafo y modificar mock_result; el nodo debe existir antes de la lógica completa

**⚠️ CRITICAL**: Sin esta fase, el grafo no compila con el nuevo flujo

- [x] T002 Add `generate_minutes` node to graph in `src/agents/meeting/agent.py`: extract_actions → generate_minutes → mock_result → END
- [x] T003 Modify `src/agents/meeting/nodes/mock_result/node.py` to NOT return `minutes` in its dict (preserve value from state)

**Checkpoint**: Grafo compila y ejecuta; generate_minutes debe devolver algo (aunque sea placeholder) para que el flujo no falle

---

## Phase 3: Caso vacío (FR-007)

**Goal**: Cuando no hay participantes, temas ni acciones extraídos, devolver mensaje fijo sin invocar LLM; nunca cadena vacía

**Independent Test**: State con participants/topics/actions vacíos o "No identificados"/"No hay temas identificados"/"No hay acciones identificadas" → minutes = "Minuta: No se identificó información procesable en la reunión."

### Implementation for FR-007

- [x] T004 Add `_is_empty_input(participants: str, topics: str, actions: str) -> bool` in `src/agents/meeting/nodes/generate_minutes/node.py`: return True if all three are empty, "No identificados", "No hay temas identificados", "No hay acciones identificadas" (or equivalent)
- [x] T005 Ensure `generate_minutes_node()` returns `{"minutes": "Minuta: No se identificó información procesable en la reunión."}` immediately when `_is_empty_input()` is True, without LLM call
- [x] T006 [P] Unit test: empty/minimal state → minutes = "Minuta: No se identificó información procesable en la reunión." (no LLM call) in `tests/unit/agents/meeting/nodes/generate_minutes/test_generate_minutes.py`

**Checkpoint**: Sin datos → mensaje fijo; nunca cadena vacía; no llamada LLM

---

## Phase 4: User Story 1 - Minuta completa (Priority: P1) 🎯 MVP

**Goal**: Generar minuta formal narrativa integrando participantes, temas y acciones cuando existan; tono profesional, español, máximo 150 palabras

**Independent Test**: Dado participantes, temas y acciones extraídos → minuta coherente ≤150 palabras con la información integrada

### Implementation for User Story 1

- [x] T007 [US1] Implement `GENERATE_MINUTES_PROMPT` in `src/agents/meeting/nodes/generate_minutes/prompt.py` (instruct: minuta narrativa continua en español; tono profesional; integrar participantes, temas y acciones; sin secciones con encabezados; máximo 150 palabras; no inventar información)
- [x] T008 [US1] Implement LLM path in `generate_minutes_node()` in `src/agents/meeting/nodes/generate_minutes/node.py`: when NOT empty, read participants, topics, actions from state; invoke ChatOpenAI (no structured output) with prompt; return `{"minutes": response_content}` (post-proceso 150 palabras en US3)
- [x] T009 [US1] Ensure prompt receives placeholders for `{participants}`, `{topics}`, `{actions}` and node passes state values (empty or "No identificados"/"No hay temas identificados"/"No hay acciones identificadas" when applicable)

**Checkpoint**: Texto con participantes, temas y acciones → minuta narrativa generada; API devuelve minutes en respuesta

---

## Phase 5: User Story 2 - Minuta con información parcial (Priority: P1)

**Goal**: Cuando solo parte de la información existe (ej. solo temas), generar minuta integrando lo disponible sin inventar secciones ni datos

**Independent Test**: Solo temas identificados (sin participantes ni acciones) → minuta coherente con la información disponible; no inventa participantes ni acciones

### Implementation for User Story 2

- [x] T010 [US2] Ensure prompt in `src/agents/meeting/nodes/generate_minutes/prompt.py` instructs: integrar solo la información disponible; no inventar participantes, temas ni acciones inexistentes; mantener coherencia con entrada parcial
- [x] T011 [US2] Ensure node in `src/agents/meeting/nodes/generate_minutes/node.py` passes participants, topics, actions to prompt without filtering (let prompt handle partial data; empty/sin-datos values are valid input)
- [x] T012 [P] [US2] Unit test: state with only topics (participants/actions empty or "No identificados"/"No hay acciones identificadas") → minutes integrates topics only, no invented sections in `tests/unit/agents/meeting/nodes/generate_minutes/test_generate_minutes.py`

**Checkpoint**: Información parcial → minuta coherente; no secciones inventadas

---

## Phase 6: User Story 3 - Respeto del límite 150 palabras (Priority: P2)

**Goal**: Minuta máximo 150 palabras; conteo por split por espacios; truncar si el LLM excede

**Independent Test**: Diferentes volúmenes de entrada → minutes nunca supera 150 palabras (conteo: split por espacios)

### Implementation for User Story 3

- [x] T013 [US3] Add `_truncate_to_word_limit(text: str, limit: int = 150) -> str` in `src/agents/meeting/nodes/generate_minutes/node.py`: split por espacios; si len(words) > limit, truncar en último límite de oración (último "." o ";") antes de palabra limit, o en palabra limit como fallback
- [x] T014 [US3] Ensure `generate_minutes_node()` applies truncation to LLM output before returning in `src/agents/meeting/nodes/generate_minutes/node.py`
- [x] T015 [P] [US3] Unit test: mock LLM returning >150 words → output ≤150 words in `tests/unit/agents/meeting/nodes/generate_minutes/test_generate_minutes.py`
- [x] T016 [P] [US3] Unit test: word count uses split by spaces (e.g. "palabra1 palabra2" = 2 words) in `tests/unit/agents/meeting/nodes/generate_minutes/test_generate_minutes.py`

**Checkpoint**: Todas las minutas ≤150 palabras; conteo correcto

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, integración E2E y validación del quickstart

- [x] T017 [P] Unit test: full state (participants, topics, actions) → minutes ≤150 words, Spanish, narrative in `tests/unit/agents/meeting/nodes/generate_minutes/test_generate_minutes.py`
- [x] T018 [P] Integration test: POST /process/text with text containing participants, topics, actions → response.minutes from generate_minutes (not mock) in `tests/integration/test_api_process_minutes.py` (or extend existing process test)
- [ ] T019 Run quickstart validation per `specs/006-generate-minutes/quickstart.md` (validación manual: curl con datos completos, parciales, vacíos; verificar UI)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA user stories
- **Phase 3 (FR-007)**: Tras Foundational — Caso vacío (early return antes de LLM)
- **Phase 4 (US1)**: Tras Phase 3 — Core generation con LLM
- **Phase 5 (US2)**: Tras US1 — Caso parcial
- **Phase 6 (US3)**: Tras US2 — Truncamiento 150 palabras
- **Polish (Phase 7)**: Depende de Phases 3–6 completas

### User Story Dependencies

- **FR-007 (Phase 3)**: Tras Foundational — Primero (evita llamada LLM innecesaria)
- **US1 (P1)**: Tras FR-007 — Core generation con LLM
- **US2 (P1)**: Tras US1 — Caso parcial (prompt + node)
- **US3 (P2)**: Tras US2 — Truncamiento 150 palabras

### Parallel Opportunities

- T006, T012, T015, T016 pueden ejecutarse en paralelo tras sus fases respectivas
- T017, T018 pueden ejecutarse en paralelo tras Phase 6

---

## Parallel Example: Phase 7

```bash
# Tras Phase 6:
Task T017: "Unit test full state narrative"
Task T018: "Integration test API process minutes"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + FR-007)

1. Phase 1: Setup
2. Phase 2: Foundational (graph + mock_result)
3. Phase 3: FR-007 (empty case — early return)
4. Phase 4: US1 (core generation)
5. Phase 5: US2 (partial data)
6. **STOP and VALIDATE**: Minuta generada con datos completos/parciales; mensaje fijo cuando vacío
7. Demo listo

### Incremental Delivery

1. Setup + Foundational → Grafo con nodo
2. Phase 3 (FR-007) → Caso vacío → Demo
3. US1 → Generación con LLM → Demo (MVP core)
4. US2 → Información parcial → Demo
5. US3 → Límite 150 palabras → Demo
6. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. FR-007 (vacío) | T004–T006 | 3 |
| 4. US1 (MVP) | T007–T009 | 3 |
| 5. US2 | T010–T012 | 3 |
| 6. US3 | T013–T016 | 4 |
| 7. Polish | T017–T019 | 3 |
| **Total** | | **19** |

**MVP scope**: Phases 1–5 (T001–T012) — 12 tasks
