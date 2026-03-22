# Tasks: Ver temas principales discutidos

**Input**: Design documents from `/specs/004-identify-topics/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para identify_topics, integración para flujo completo).

**Organization**: Tareas agrupadas por user story; US1–US4 se implementan incrementalmente (US1–US3 en el mismo nodo; US4 en UI).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3, US4)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001/002/003

---

## Phase 1: Setup (Estructura del nodo)

**Purpose**: Crear la estructura del nodo identify_topics según Principio II (nodos autocontenidos)

- [x] T001 Create `src/agents/meeting/nodes/identify_topics/` directory with `__init__.py`, `node.py` (stub returning `{"topics": "No hay temas identificados"}`), `prompt.py` (stub)

---

## Phase 2: Foundational (Integración en el grafo)

**Purpose**: Integrar identify_topics en el grafo y modificar mock_result; el nodo debe existir antes de la lógica completa

**⚠️ CRITICAL**: Sin esta fase, el grafo no compila con el nuevo flujo

- [x] T002 Add `identify_topics` node to graph in `src/agents/meeting/agent.py`: extract_participants → identify_topics → mock_result → END
- [x] T003 Modify `src/agents/meeting/nodes/mock_result/node.py` to NOT return `topics` in its dict (preserve value from state)

**Checkpoint**: Grafo compila y ejecuta; identify_topics debe devolver algo (aunque sea placeholder) para que el flujo no falle

---

## Phase 3: User Story 1 - Ver temas principales (Priority: P1) 🎯 MVP

**Goal**: Extraer entre 3 y 5 temas principales del texto; separados por punto y coma; orden por primera aparición

**Independent Test**: Texto con "presupuesto, plazos y recursos..." → topics incluye 3-5 temas separados por "; "; orden coherente

### Implementation for User Story 1

- [x] T004 [US1] Define `TopicsExtraction` Pydantic model (topics: list[str]) in `src/agents/meeting/nodes/identify_topics/node.py`
- [x] T005 [US1] Implement `IDENTIFY_TOPICS_PROMPT` in `src/agents/meeting/nodes/identify_topics/prompt.py` (instruct: 3-5 temas, granularidad apropiada, excluir genéricos, consolidar solapados preferiendo variante específica)
- [x] T006 [US1] Implement `identify_topics_node()` in `src/agents/meeting/nodes/identify_topics/node.py`: ChatOpenAI (or configured LLM) with `with_structured_output(TopicsExtraction)`, invoke with raw_text, post-process: sort by first occurrence in raw_text, format as `"; ".join(...)`, return `{"topics": ...}` or `"No hay temas identificados"` if empty

**Checkpoint**: Texto con temas → lista extraída 3-5; separador punto y coma; API devuelve topics en respuesta

---

## Phase 4: User Story 2 - Pocos o cero temas (Priority: P2)

**Goal**: Cuando hay menos de 3 temas o 0 temas, retornar los disponibles sin forzar relleno; 0 temas → "No hay temas identificados"

**Independent Test**: Texto "Reunión de coordinación." → topics = "No hay temas identificados"; texto con 2 temas → exactamente 2 temas sin inventar

### Implementation for User Story 2

- [x] T007 [US2] Ensure empty/zero topics case returns `"No hay temas identificados"` in `src/agents/meeting/nodes/identify_topics/node.py` (verify T006 handles: empty list → "No hay temas identificados"; add explicit check if needed)
- [x] T008 [US2] Ensure prompt instructs LLM to return 1-5 topics max, never invent; if fewer identifiable, return only those in `src/agents/meeting/nodes/identify_topics/prompt.py`
- [x] T009 [P] [US2] Unit test: text with no identifiable topics → "No hay temas identificados" in `tests/unit/agents/meeting/nodes/identify_topics/test_identify_topics.py`

**Checkpoint**: Texto sin temas → "No hay temas identificados"; 2 temas → exactamente 2; nunca cadena vacía

---

## Phase 5: User Story 3 - Granularidad y consolidación (Priority: P3)

**Goal**: Evitar temas genéricos ("Reunión de trabajo"); consolidar solapados ("Presupuesto" + "Presupuesto Q2" → "Presupuesto Q2"); orden por primera aparición

**Independent Test**: "Sprint 12 y bugs del módulo de facturación" → no "Reunión de trabajo"; "Presupuesto Q2... presupuesto..." → un solo tema "Presupuesto Q2"

### Implementation for User Story 3

- [x] T010 [US3] Add post-processing `_sort_by_first_occurrence(topics: list[str], raw_text: str)` in `src/agents/meeting/nodes/identify_topics/node.py` (same pattern as extract_participants)
- [x] T011 [US3] Verify prompt in `src/agents/meeting/nodes/identify_topics/prompt.py` instructs: avoid generic topics ("Reunión", "Discusión general"); consolidate overlapping topics preferring more specific variant
- [x] T012 [P] [US3] Unit test: overlapping topics ("Presupuesto", "Presupuesto Q2") → consolidated in `tests/unit/agents/meeting/nodes/identify_topics/test_identify_topics.py`
- [x] T013 [P] [US3] Unit test: generic text → no "Reunión de trabajo"; specific topics included in `tests/unit/agents/meeting/nodes/identify_topics/test_identify_topics.py`

**Checkpoint**: Granularidad apropiada; consolidación; orden por primera aparición según spec

---

## Phase 6: User Story 4 - Loader durante análisis (Priority: P1)

**Goal**: Loader visible durante procesamiento; ocultar y mostrar error cuando falla

**Independent Test**: Pulsar Procesar → loader visible hasta fin; simular error (API caída) → loader se oculta, mensaje de error visible

### Implementation for User Story 4

- [x] T014 [US4] Verify `show_progress=True` on `process_btn.click()` in `src/ui/app.py` displays loader during API call (Gradio default)
- [x] T015 [US4] Verify error handlers in `process_meeting_text()` and `process_meeting_file()` in `src/ui/app.py` return error message to output (loader auto-hides when function returns); add explicit loader/error UX if current behavior insufficient per Gradio skill

**Checkpoint**: Loader visible durante procesamiento; errores muestran mensaje claro; loader se oculta al fallar

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, integración E2E y validación del quickstart

- [x] T016 [P] Unit test: text with multiple topics → 3-5 topics, semicolon-separated, order by first appearance in `tests/unit/agents/meeting/nodes/identify_topics/test_identify_topics.py`
- [x] T017 [P] Unit test: text with 2 topics → exactly 2, no filler in `tests/unit/agents/meeting/nodes/identify_topics/test_identify_topics.py`
- [x] T018 [P] Integration test: POST /process/text with text containing topics → response.topics from identify_topics (not mock) in `tests/integration/test_api_process_topics.py` (or extend existing process test)
- [ ] T019 Run quickstart validation per `specs/004-identify-topics/quickstart.md` (validación manual: curl con texto con temas, sin temas, verificar UI loader cuando API está levantada)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA user stories
- **User Stories (Phase 3–6)**: Dependen de Foundational
  - US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5): incremental en el mismo nodo
  - US4 (Phase 6): independiente (UI); puede validarse en paralelo tras Phase 2
- **Polish (Phase 7)**: Depende de US1–US4 completas

### User Story Dependencies

- **US1 (P1)**: Tras Phase 2 — Core extraction
- **US2 (P2)**: Tras US1 — Casos vacío/pocos (simple extensión)
- **US3 (P3)**: Tras US2 — Post-proceso (orden), prompt (genéricos, consolidación)
- **US4 (P1)**: Tras Phase 2 — Verificación UI (loader); independiente del nodo

### Parallel Opportunities

- T009, T012, T013 pueden ejecutarse en paralelo tras Phase 5
- T016, T017, T018 pueden ejecutarse en paralelo tras Phase 6
- T014, T015 (US4) pueden ejecutarse en paralelo tras Phase 2 si se prioriza loader

---

## Parallel Example: Phase 4–5

```bash
# Tras T008:
Task T009: "Unit test no topics → No hay temas identificados"
# Phase 5, tras T011:
Task T012: "Unit test consolidate overlapping topics"
Task T013: "Unit test avoid generic topics"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4)

1. Phase 1: Setup
2. Phase 2: Foundational (graph + mock_result)
3. Phase 3: US1 (full extraction logic)
4. Phase 6: US4 (verify loader)
5. **STOP and VALIDATE**: Temas extraídos; loader visible; errores mostrados
6. Demo listo

### Incremental Delivery

1. Setup + Foundational → Grafo con nodo
2. US1 → Extracción básica → Demo (MVP core)
3. US2 → "No hay temas identificados", pocos temas → Demo
4. US3 → Granularidad, consolidación, orden → Demo
5. US4 → Loader verificado → Demo
6. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. US1 (MVP) | T004–T006 | 3 |
| 4. US2 | T007–T009 | 3 |
| 5. US3 | T010–T013 | 4 |
| 6. US4 | T014, T015 | 2 |
| 7. Polish | T016–T019 | 4 |
| **Total** | | **19** |

**MVP scope**: Phases 1–3 + 6 (T001–T006, T014–T015) — 8 tasks
