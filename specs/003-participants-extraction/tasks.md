# Tasks: Ver extracción de participantes

**Input**: Design documents from `/specs/003-participants-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Incluidos (plan.md especifica tests unitarios para extract_participants).

**Organization**: Tareas agrupadas por user story; US1–US3 se implementan incrementalmente en el mismo nodo.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: User story (US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Path Conventions

- Proyecto único: `src/`, `tests/` en la raíz del repositorio
- Estructura heredada de 001-hello-world-e2e

---

## Phase 1: Setup (Estructura del nodo)

**Purpose**: Crear la estructura del nodo extract_participants según Principio II (nodos autocontenidos)

- [x] T001 Create `src/agents/meeting/nodes/extract_participants/` directory with `__init__.py`, `node.py` (stub returning `{"participants": "No identificados"}`), `prompt.py` (stub)

---

## Phase 2: Foundational (Integración en el grafo)

**Purpose**: Integrar extract_participants en el grafo y modificar mock_result; el nodo debe existir antes de la lógica completa

**⚠️ CRITICAL**: Sin esta fase, el grafo no compila con el nuevo flujo

- [x] T002 Add `extract_participants` node to graph in `src/agents/meeting/agent.py`: preprocess → extract_participants → mock_result → END
- [x] T003 Modify `src/agents/meeting/nodes/mock_result/node.py` to NOT return `participants` in its dict (preserve value from state)

**Checkpoint**: Grafo compila y ejecuta; extract_participants debe devolver algo (aunque sea placeholder) para que el flujo no falle

---

## Phase 3: User Story 1 - Ver participantes identificados (Priority: P1) 🎯 MVP

**Goal**: Extraer nombres de participantes del texto; excluir términos genéricos ("persona", "alguien"); listar por comas

**Independent Test**: Texto con "Juan, María y Pedro asistieron..." → participants = "Juan, María, Pedro"; texto con "persona" → no incluir "persona"

### Implementation for User Story 1

- [x] T004 [US1] Define `ParticipantsExtraction` Pydantic model (participants: list[str]) in `src/agents/meeting/nodes/extract_participants/node.py`
- [x] T005 [US1] Implement `EXTRACT_PARTICIPANTS_PROMPT` in `src/agents/meeting/nodes/extract_participants/prompt.py` (instruct: extraer nombres propios, excluir "persona", "alguien", "un participante", excluir títulos)
- [x] T006 [US1] Implement `extract_participants_node()` in `src/agents/meeting/nodes/extract_participants/node.py`: ChatOpenAI (or configured LLM) with `with_structured_output(ParticipantsExtraction)`, invoke with raw_text, return `{"participants": ", ".join(...) or "No identificados"}`

**Checkpoint**: Texto con nombres → lista extraída; texto con "persona" → excluido; API devuelve participants en respuesta

---

## Phase 4: User Story 2 - Texto sin participantes (Priority: P2)

**Goal**: Cuando no hay nombres identificables, devolver "No identificados" (nunca cadena vacía)

**Independent Test**: Texto "Se discutió el presupuesto. Hubo acuerdo." → participants = "No identificados"

### Implementation for User Story 2

- [x] T007 [US2] Ensure empty/zero participants case returns `"No identificados"` in `src/agents/meeting/nodes/extract_participants/node.py` (verify T006 already handles: `", ".join(names) if names else "No identificados"`; add explicit check if needed)
- [x] T008 [P] [US2] Unit test: text with no names → "No identificados" in `tests/unit/agents/meeting/nodes/extract_participants/test_extract_participants.py`

**Checkpoint**: Texto sin nombres → "No identificados"; nunca cadena vacía

---

## Phase 5: User Story 3 - Deduplicación y variantes (Priority: P3)

**Goal**: Deduplicar participantes; preferir variante más completa; orden por primera aparición; excluir títulos

**Independent Test**: "Laura García propuso... Laura acordó..." → participants incluye "Laura García" una vez; "Dr. Pérez asistió" → "Pérez" o nombre sin título

### Implementation for User Story 3

- [x] T009 [US3] Add post-processing in `src/agents/meeting/nodes/extract_participants/node.py`: sort by first occurrence in raw_text (str.find); instruction in prompt for dedup + prefer full name (LLM does it; post-process enforces order)
- [x] T010 [P] [US3] Unit test: text with "Juan Pérez" and "Juan" → single entry, full name preferred; order by first appearance in `tests/unit/agents/meeting/nodes/extract_participants/test_extract_participants.py`
- [x] T011 [P] [US3] Unit test: "Dr. García", "Ing. López" → names without titles in `tests/unit/agents/meeting/nodes/extract_participants/test_extract_participants.py`

**Checkpoint**: Dedup, orden, exclusión de títulos funcionando según spec

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Tests adicionales, integración E2E y validación del quickstart

- [x] T012 [P] Unit test: text with "Juan, María y Pedro" → participants includes all three; excludes "persona" in `tests/unit/agents/meeting/nodes/extract_participants/test_extract_participants.py`
- [x] T013 [P] Integration test: POST /process/text with text containing names → response.participants from extract_participants (not mock) in `tests/integration/test_api_process_participants.py`
- [x] T014 Run quickstart validation per `specs/003-participants-extraction/quickstart.md` (validación manual: curl con texto con nombres y sin nombres cuando API está levantada)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias — iniciar de inmediato
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEA user stories
- **User Stories (Phase 3–5)**: Dependen de Foundational
  - US1 (Phase 3) → US2 (Phase 4) → US3 (Phase 5): incremental en el mismo nodo
- **Polish (Phase 6)**: Depende de US1–US3 completas

### User Story Dependencies

- **US1 (P1)**: Tras Phase 2 — Core extraction
- **US2 (P2)**: Tras US1 — Caso vacío (simple extensión)
- **US3 (P3)**: Tras US2 — Post-proceso (orden, dedup, títulos)

### Parallel Opportunities

- T008, T010, T011, T012 pueden ejecutarse en paralelo tras completar Phase 5
- T013, T014 pueden ejecutarse en paralelo tras Phase 5

---

## Parallel Example: Phase 4–5

```bash
# Tras T007:
Task T008: "Unit test no names → No identificados"
# Phase 5, tras T009:
Task T010: "Unit test dedup + full name"
Task T011: "Unit test exclude titles"
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1: Setup
2. Phase 2: Foundational (graph + mock_result)
3. Phase 3: US1 (full extraction logic)
4. **STOP and VALIDATE**: Texto con nombres → lista; texto con "persona" → excluido
5. Demo listo

### Incremental Delivery

1. Setup + Foundational → Grafo con nodo
2. US1 → Extracción básica → Demo (MVP)
3. US2 → "No identificados" → Demo
4. US3 → Dedup, orden, títulos → Demo
5. Polish → Tests + quickstart

### Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 1. Setup | T001 | 1 |
| 2. Foundational | T002, T003 | 2 |
| 3. US1 (MVP) | T004–T006 | 3 |
| 4. US2 | T007, T008 | 2 |
| 5. US3 | T009–T011 | 3 |
| 6. Polish | T012, T013, T014 | 3 |
| **Total** | | **14** |

**MVP scope**: Phases 1–3 (T001–T006) — 6 tasks
