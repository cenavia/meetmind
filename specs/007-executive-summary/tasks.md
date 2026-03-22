# Tasks: Ver resumen ejecutivo

**Input**: Design documents from `/specs/007-executive-summary/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para create_summary, integración para flujo completo; tests UI para botón Procesar).

**Organization**: Tareas agrupadas por user story; US1–US2 se implementan en el nodo create_summary; US3 en la UI Gradio.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001-006

---

## Phase 1: Setup (Estructura del nodo)

**Purpose**: Crear la estructura del nodo create_summary según Principio II (nodos autocontenidos)

- [x] T001 Create `src/agents/meeting/nodes/create_summary/` directory with `__init__.py`, `node.py` (stub returning `{"executive_summary": "Resumen: No se identificó información procesable en la reunión."}`), `prompt.py` (stub)

---

## Phase 2: Foundational (Integración en el grafo)

**Purpose**: Integrar create_summary en el grafo y modificar mock_result; el nodo debe existir antes de la lógica completa

**⚠️ CRITICAL**: Sin esta fase, el grafo no compila con el nuevo flujo

- [x] T002 Add `create_summary` node to graph in `src/agents/meeting/agent.py`: generate_minutes → create_summary → mock_result → END
- [x] T003 Modify `src/agents/meeting/nodes/mock_result/node.py` to NOT return `executive_summary` in its dict (preserve value from state)

**Checkpoint**: Grafo compila y ejecuta; create_summary debe devolver algo (aunque sea placeholder) para que el flujo no falle

---

## Phase 3: Caso vacío (FR-008)

**Goal**: Cuando no hay participantes, temas ni acciones extraídos, devolver mensaje fijo sin invocar LLM; nunca cadena vacía

**Independent Test**: State con participants/topics/actions vacíos o "No identificados"/"No hay temas identificados"/"No hay acciones identificadas" → executive_summary = "Resumen: No se identificó información procesable en la reunión."

### Implementation for FR-008

- [x] T004 Add `_is_empty_input(participants: str, topics: str, actions: str) -> bool` in `src/agents/meeting/nodes/create_summary/node.py`: return True if all three are empty or contain only "sin datos" literals (e.g. "No identificados", "No hay temas identificados", "No hay acciones identificadas")
- [x] T005 Ensure `create_summary_node()` returns `{"executive_summary": "Resumen: No se identificó información procesable en la reunión."}` immediately when `_is_empty_input()` is True, without LLM call
- [x] T006 [P] [US1] Unit test: empty/minimal state → executive_summary = "Resumen: No se identificó información procesable en la reunión." (no LLM call) in `tests/unit/agents/meeting/nodes/create_summary/test_create_summary.py`

**Checkpoint**: Sin datos → mensaje fijo; nunca cadena vacía; no llamada LLM

---

## Phase 4: User Story 1 - Resumen ejecutivo con decisiones (Priority: P1) 🎯 MVP

**Goal**: Generar resumen ejecutivo ≤30 palabras integrando participantes, temas, acciones y minuta; enfocado en decisiones, acciones críticas, conclusiones principales; español

**Independent Test**: Dado participantes, temas, acciones y minuta → resumen coherente ≤30 palabras con decisiones/acciones clave

### Implementation for User Story 1

- [x] T007 [US1] Implement `CREATE_SUMMARY_PROMPT` in `src/agents/meeting/nodes/create_summary/prompt.py` (instruct: resumen español; máximo 30 palabras; decisiones tomadas, acciones críticas, conclusiones principales; síntesis clara y accionable; placeholders {participants}, {topics}, {actions}, {minutes})
- [x] T008 [US1] Implement LLM path in `create_summary_node()` in `src/agents/meeting/nodes/create_summary/node.py`: when NOT empty, read participants, topics, actions, minutes from state; invoke ChatOpenAI with prompt; return `{"executive_summary": response_content}` (word limit handling in Phase 5)
- [x] T009 [US1] Add `_ensure_word_limit(text: str, limit: int = 30) -> str` in `src/agents/meeting/nodes/create_summary/node.py`: if words > limit, retry with adjusted prompt (máx. 2 reintentos) or truncate at word 30 as fallback; word count = split by spaces
- [x] T010 [US1] Ensure `create_summary_node()` applies `_ensure_word_limit` to LLM output before returning in `src/agents/meeting/nodes/create_summary/node.py`
- [x] T011 [P] [US1] Unit test: full state (participants, topics, actions, minutes) → executive_summary ≤30 words, Spanish, focuses on decisions/actions in `tests/unit/agents/meeting/nodes/create_summary/test_create_summary.py`

**Checkpoint**: Resumen generado con LLM; ≤30 palabras; español; decisiones/acciones/conclusiones

---

## Phase 5: User Story 2 - Resumen informativo (Priority: P1)

**Goal**: Para reuniones informativas (sin decisiones explícitas), sintetizar temas principales con tono profesional

**Independent Test**: Solo temas, sin acciones ni decisiones → resumen sintetiza temas principales; tono profesional

### Implementation for User Story 2

- [x] T012 [US2] Ensure prompt in `src/agents/meeting/nodes/create_summary/prompt.py` instructs: para reuniones informativas, sintetizar temas principales; mantener tono profesional; no inventar decisiones/acciones inexistentes
- [x] T013 [P] [US2] Unit test: state with only topics (informative meeting) → executive_summary synthesizes topics, professional tone in `tests/unit/agents/meeting/nodes/create_summary/test_create_summary.py`

**Checkpoint**: Reuniones informativas → resumen con temas principales; tono profesional

---

## Phase 6: Límite 30 palabras (retry + truncate fallback)

**Goal**: Si el LLM excede 30 palabras: retry con prompt ajustado (máx. 2 reintentos); fallback truncar en palabra 30; conteo: split por espacios

**Independent Test**: Mock LLM returning >30 words → output ≤30 words (via retry or truncate)

### Implementation

- [x] T014 [US1] Implement retry logic in `_ensure_word_limit` or `create_summary_node()` in `src/agents/meeting/nodes/create_summary/node.py`: on first LLM response >30 words, invoke again with prompt "Acorta el siguiente texto a máximo 30 palabras: {texto}"; máx. 2 retries; if still >30, truncate at word 30
- [x] T015 [P] [US1] Unit test: mock LLM returning >30 words → output ≤30 words in `tests/unit/agents/meeting/nodes/create_summary/test_create_summary.py`
- [x] T016 [P] [US1] Unit test: word count uses split by spaces (e.g. "palabra1 palabra2" = 2 words) in `tests/unit/agents/meeting/nodes/create_summary/test_create_summary.py`

**Checkpoint**: Todas las salidas ≤30 palabras; retry o truncate según research.md

---

## Phase 7: User Story 3 - Botón Procesar desactivado hasta Limpiar (Priority: P1)

**Goal**: Tras clic en Procesar, el botón se desactiva inmediatamente; permanece desactivado hasta clic en Limpiar; tras Limpiar y añadir contenido, Procesar se reactiva

**Independent Test**: Cargar archivo/texto → Procesar → botón desactivado; Limpiar → añadir contenido → botón activado

### Implementation for User Story 3

- [x] T017 [US3] Create wrapper in `src/ui/app.py`: `on_process(text, file)` that calls `process_dispatch(text, file)` and returns `(result, gr.update(interactive=False))` for process_btn
- [x] T018 [US3] Modify `process_btn.click()` in `src/ui/app.py`: add `process_btn` to outputs; use `on_process` as handler so button disables immediately on click
- [x] T019 [US3] Verify `do_clear` and `update_inputs` (text_input.change, file_input.change) correctly re-enable process_btn when user adds content after clearing (no changes needed if flow already correct per research.md)
- [x] T020 [P] [US3] Manual or UI test: Procesar → button disabled; Limpiar → add content → button enabled (document in quickstart verification)

**Checkpoint**: Procesar desactivado al clic; Limpiar reactiva flujo; cambio de contenido reactiva Procesar

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, integración E2E y validación del quickstart

- [x] T021 [P] Integration test: POST /process/text with text containing participants, topics, actions → response.executive_summary from create_summary (not mock) in `tests/integration/test_api_process_summary.py` (or extend existing process test)
- [ ] T022 Run quickstart validation per `specs/007-executive-summary/quickstart.md` (validación manual: curl con datos completos, vacíos; verificar UI con Procesar desactivado tras procesar)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA user stories
- **Phase 3 (FR-008)**: Tras Foundational — Caso vacío (early return antes de LLM)
- **Phase 4 (US1)**: Tras Phase 3 — Core generation con LLM
- **Phase 5 (US2)**: Tras US1 — Caso informativo (prompt)
- **Phase 6**: Tras US1 — Límite 30 palabras (retry + truncate)
- **Phase 7 (US3)**: Independiente de Phases 4–6 — UI; puede desarrollarse en paralelo
- **Polish (Phase 8)**: Depende de Phases 4–7 completas

### User Story Dependencies

- **FR-008 (Phase 3)**: Tras Foundational — Primero (evita llamada LLM innecesaria)
- **US1 (P1)**: Tras FR-008 — Core generation + word limit
- **US2 (P1)**: Tras US1 — Caso informativo
- **US3 (P1)**: Independiente del nodo — UI Gradio

### Parallel Opportunities

- T006, T011, T013, T015, T016 pueden ejecutarse en paralelo tras sus fases respectivas
- T021 puede ejecutarse tras Phase 7
- Phase 7 (US3) puede desarrollarse en paralelo con Phase 4–6 si hay dos desarrolladores

---

## Parallel Example: Phase 8

```bash
# Tras Phase 7:
Task T021: "Integration test API process summary"
Task T022: "Quickstart validation"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 3 + FR-008)

1. Phase 1: Setup
2. Phase 2: Foundational (graph + mock_result)
3. Phase 3: FR-008 (empty case — early return)
4. Phase 4: US1 (core generation)
5. Phase 5: US2 (informative meetings)
6. Phase 6: Word limit (retry + truncate)
7. Phase 7: US3 (UI Procesar desactivado)
8. **STOP and VALIDATE**: Resumen generado; Procesar desactivado correctamente
9. Demo listo

### Incremental Delivery

1. Setup + Foundational → Grafo con nodo
2. Phase 3 (FR-008) → Caso vacío → Demo
3. Phase 4 (US1) → Generación con LLM → Demo (MVP core)
4. Phase 5 (US2) → Caso informativo → Demo
5. Phase 6 → Límite 30 palabras → Demo
6. Phase 7 (US3) → UI Procesar/Limpiar → Demo completo
7. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. FR-008 (vacío) | T004–T006 | 3 |
| 4. US1 (MVP core) | T007–T011 | 5 |
| 5. US2 | T012, T013 | 2 |
| 6. Word limit | T014–T016 | 3 |
| 7. US3 (UI) | T017–T020 | 4 |
| 8. Polish | T021, T022 | 2 |
| **Total** | | **22** |

**MVP scope**: Phases 1–7 (T001–T020) — 20 tasks
