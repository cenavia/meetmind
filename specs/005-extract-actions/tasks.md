# Tasks: Ver acciones acordadas con responsables

**Input**: Design documents from `/specs/005-extract-actions/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para extract_actions, integración para flujo completo).

**Organization**: Tareas agrupadas por user story; US1–US4 se implementan incrementalmente en el mismo nodo extract_actions.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3, US4)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001-004

---

## Phase 1: Setup (Estructura del nodo)

**Purpose**: Crear la estructura del nodo extract_actions según Principio II (nodos autocontenidos)

- [x] T001 Create `src/agents/meeting/nodes/extract_actions/` directory with `__init__.py`, `node.py` (stub returning `{"actions": "No hay acciones identificadas"}`), `prompt.py` (stub)

---

## Phase 2: Foundational (Integración en el grafo)

**Purpose**: Integrar extract_actions en el grafo y modificar mock_result; el nodo debe existir antes de la lógica completa

**⚠️ CRITICAL**: Sin esta fase, el grafo no compila con el nuevo flujo

- [x] T002 Add `extract_actions` node to graph in `src/agents/meeting/agent.py`: identify_topics → extract_actions → mock_result → END
- [x] T003 Modify `src/agents/meeting/nodes/mock_result/node.py` to NOT return `actions` in its dict (preserve value from state)

**Checkpoint**: Grafo compila y ejecuta; extract_actions debe devolver algo (aunque sea placeholder) para que el flujo no falle

---

## Phase 3: User Story 1 - Acciones con responsables explícitos (Priority: P1) 🎯 MVP

**Goal**: Extraer acciones acordadas con responsable asignado cuando es identificable; formato "acción | responsable"

**Independent Test**: Texto "María enviará el informe antes del viernes" → actions incluye "Enviar informe antes del viernes | María"

### Implementation for User Story 1

- [x] T004 [US1] Define `ActionItem` and `ActionsExtraction` Pydantic models in `src/agents/meeting/nodes/extract_actions/node.py` (ActionItem: action, responsible; ActionsExtraction: actions: list[ActionItem])
- [x] T005 [US1] Implement `EXTRACT_ACTIONS_PROMPT` in `src/agents/meeting/nodes/extract_actions/prompt.py` (instruct: extraer pares acción-responsable; variantes lingüísticas "se encargará", "debe", "comprometió a"; responsable solo por nombre propio; varios responsables → primer nombre; evitar "|" y ";" en salida)
- [x] T006 [US1] Implement `extract_actions_node()` in `src/agents/meeting/nodes/extract_actions/node.py`: ChatOpenAI with `with_structured_output(ActionsExtraction)`, invoke with raw_text, post-process: sanitize "|" and ";" in action/responsible, sort by first occurrence in raw_text, format as `"; ".join(f"{a.action} | {a.responsible}" for a in ordered)`, return `{"actions": ...}` or `"No hay acciones identificadas"` if empty

**Checkpoint**: Texto con acción explícita y responsable → par extraído en formato "acción | responsable"; API devuelve actions en respuesta

---

## Phase 4: User Story 2 - Acciones sin responsable (Priority: P1)

**Goal**: Cuando el responsable no es identificable, usar "Por asignar"; cargo sin nombre → "Por asignar"

**Independent Test**: Texto "Se debe revisar el contrato" → actions incluye "Revisar el contrato | Por asignar"

### Implementation for User Story 2

- [x] T007 [US2] Ensure prompt in `src/agents/meeting/nodes/extract_actions/prompt.py` instructs: sin responsable explícito o solo cargo → "Por asignar"; nunca inventar responsable
- [x] T008 [US2] Ensure node in `src/agents/meeting/nodes/extract_actions/node.py` maps empty/missing responsible from LLM to "Por asignar" before formatting
- [x] T009 [P] [US2] Unit test: text "Se debe revisar el contrato" → actions contains "Revisar el contrato | Por asignar" in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`

**Checkpoint**: Acción sin responsable → "Por asignar"; nunca responsable inventado

---

## Phase 5: User Story 3 - Múltiples acciones con formato consistente (Priority: P2)

**Goal**: Múltiples pares separados por punto y coma; orden por primera aparición; consolidar redundantes preferiendo variante más específica; reformular para evitar "|" y ";"

**Independent Test**: Texto con varias acciones → cada par "acción | responsable"; pares separados por "; "; orden coherente

### Implementation for User Story 3

- [x] T010 [US3] Add `_sort_by_first_occurrence(items: list[ActionItem], raw_text: str)` in `src/agents/meeting/nodes/extract_actions/node.py` (order by first occurrence of action text in raw_text)
- [x] T011 [US3] Add `_sanitize_for_format(text: str) -> str` in `src/agents/meeting/nodes/extract_actions/node.py` to replace or remove "|" and ";" in action/responsible before formatting (preserve meaning)
- [x] T012 [US3] Ensure prompt in `src/agents/meeting/nodes/extract_actions/prompt.py` instructs: acciones redundantes → consolidar preferiendo variante más específica; nunca incluir "|" ni ";" en acción ni responsable
- [x] T013 [P] [US3] Unit test: multiple actions → format "acción | responsable; acción2 | responsable2", order by first appearance in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`

**Checkpoint**: Múltiples acciones con formato correcto; orden; caracteres especiales sanitizados

---

## Phase 6: User Story 4 - Sin acciones identificables (Priority: P2)

**Goal**: Cuando no hay acciones identificables, retornar "No hay acciones identificadas" (nunca cadena vacía)

**Independent Test**: Texto "Reunión de brainstorming sin acuerdos" → actions = "No hay acciones identificadas"

### Implementation for User Story 4

- [x] T014 [US4] Ensure empty/zero actions case returns `"No hay acciones identificadas"` in `src/agents/meeting/nodes/extract_actions/node.py` (empty list, empty raw_text, or LLM returns empty → "No hay acciones identificadas")
- [x] T015 [US4] Ensure prompt in `src/agents/meeting/nodes/extract_actions/prompt.py` instructs: no inventar acciones; sin acuerdos identificables → lista vacía
- [x] T016 [P] [US4] Unit test: text with no actions → "No hay acciones identificadas" in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`

**Checkpoint**: Sin acciones → "No hay acciones identificadas"; nunca cadena vacía; no inventar acciones

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, integración E2E y validación del quickstart

- [x] T017 [P] Unit test: text "María enviará el informe antes del viernes" → "Enviar informe antes del viernes | María" in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`
- [x] T018 [P] Unit test: text "María y Pedro se encargarán del informe" → first responsible (María) in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`
- [x] T019 [P] Unit test: text "El gerente enviará el resumen" → "Por asignar" as responsible in `tests/unit/agents/meeting/nodes/extract_actions/test_extract_actions.py`
- [x] T020 [P] Integration test: POST /process/text with text containing actions → response.actions from extract_actions (not mock) in `tests/integration/test_api_process_actions.py` (or extend existing process test)
- [ ] T021 Run quickstart validation per `specs/005-extract-actions/quickstart.md` (validación manual: curl con texto con acciones, sin acciones, Por asignar, verificar UI)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA user stories
- **User Stories (Phase 3–6)**: Dependen de Foundational
  - US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5) → US4 (Phase 6): incremental en el mismo nodo
- **Polish (Phase 7)**: Depende de US1–US4 completas

### User Story Dependencies

- **US1 (P1)**: Tras Phase 2 — Core extraction con responsable
- **US2 (P1)**: Tras US1 — Caso "Por asignar" (prompt + node)
- **US3 (P2)**: Tras US2 — Formato múltiple, orden, sanitización
- **US4 (P2)**: Tras US3 — Caso sin acciones

### Parallel Opportunities

- T009, T013, T016 pueden ejecutarse en paralelo tras sus fases respectivas
- T017, T018, T019, T020 pueden ejecutarse en paralelo tras Phase 6

---

## Parallel Example: Phase 7

```bash
# Tras Phase 6:
Task T017: "Unit test explicit responsible"
Task T018: "Unit test multiple responsible → first"
Task T019: "Unit test role only → Por asignar"
Task T020: "Integration test API process actions"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Phase 1: Setup
2. Phase 2: Foundational (graph + mock_result)
3. Phase 3: US1 (core extraction)
4. Phase 4: US2 (Por asignar)
5. **STOP and VALIDATE**: Acciones extraídas con formato correcto; Por asignar cuando aplique
6. Demo listo

### Incremental Delivery

1. Setup + Foundational → Grafo con nodo
2. US1 → Extracción con responsable → Demo (MVP core)
3. US2 → Por asignar → Demo
4. US3 → Múltiples, formato, orden, sanitización → Demo
5. US4 → No hay acciones → Demo
6. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. US1 (MVP) | T004–T006 | 3 |
| 4. US2 | T007–T009 | 3 |
| 5. US3 | T010–T013 | 4 |
| 6. US4 | T014–T016 | 3 |
| 7. Polish | T017–T021 | 5 |
| **Total** | | **21** |

**MVP scope**: Phases 1–4 (T001–T009) — 9 tasks
