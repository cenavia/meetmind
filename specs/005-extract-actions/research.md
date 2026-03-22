# Research: Ver acciones acordadas con responsables

**Feature**: 005-extract-actions | **Date**: 2026-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001-004), la Constitución y la spec clarificada. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Extracción con LLM vs heurística (regex, patterns)

**Decisión**: Usar LLM con salida estructurada (Pydantic) para identificar acciones y responsables.

**Rationale**: Las acciones requieren comprensión semántica: variantes lingüísticas ("se encargará", "debe", "comprometió a"), acciones implícitas, consolidación de redundantes, asociación responsable. Las reglas de la spec (varios responsables → primer nombre; cargo → "Por asignar"; reformular caracteres especiales) son mejor manejadas por un LLM con prompt especializado.

**Alternativas consideradas**:
- Regex o patterns para "X enviará", "Y debe...": No captura implícitos ni variantes; difícil consolidar redundantes. Rechazada.
- NER + reglas: Más complejo; asociar entidades a verbos de compromiso es frágil. Rechazada para MVP.

---

## 2. Structured output con Pydantic

**Decisión**: Definir un modelo Pydantic (ej. `ActionsExtraction`) con `actions: list[dict]` o `list[tuple]` con acción y responsable. Post-procesar en el nodo: ordenar por primera aparición en raw_text, formatear como "acción | responsable; acción2 | responsable2", sanitizar caracteres "|" y ";", devolver "No hay acciones identificadas" si lista vacía.

**Rationale**: LangChain soporta `with_structured_output()` con Pydantic. Un modelo con `list[ActionItem]` donde `ActionItem` tiene `action: str` y `responsible: str` permite validación y post-proceso limpio.

**Alternativas consideradas**:
- JSON schema sin Pydantic: Funcional pero Pydantic integra mejor.
- Salida en texto libre con formato "acción | responsable": Requiere parsing frágil; rechazada.

---

## 3. Orden por primera aparición

**Decisión**: El prompt instruye al LLM a devolver pares acción-responsable; el nodo post-procesa para ordenar por primera aparición de la acción en `raw_text` (usando `str.find()` o similar).

**Rationale**: Igual patrón que identify_topics y extract_participants. El LLM puede no respetar orden; es más robusto aplicar la regla en código.

---

## 4. Sanitización de "|" y ";"

**Decisión**: Tras obtener la lista de pares del LLM, el nodo reemplaza "|" y ";" dentro de acción o responsable por alternativas (ej. coma, guion) o reformula si el LLM no lo hizo. El prompt instruye explícitamente al LLM a evitar esos caracteres en la salida.

**Rationale**: La spec exige reformular para preservar el significado. Instruir en el prompt es la primera línea; post-proceso como fallback si el LLM incluye caracteres prohibidos.

**Alternativas consideradas**:
- Escapado (ej. "\|"): La spec eligió reformular; mantener consistencia.
- Delimitadores alternativos: Aumenta complejidad; rechazada.

---

## 5. Caso "No hay acciones identificadas"

**Decisión**: Si el LLM devuelve lista vacía o el texto es muy corto/vacío, el nodo retorna `actions: "No hay acciones identificadas"` (nunca cadena vacía).

**Rationale**: Clarificación de la spec: siempre texto explícito cuando 0 acciones.

---

## 6. Integración en el grafo

**Decisión**: Insertar `extract_actions` entre `identify_topics` y `mock_result`. `mock_result` deja de incluir `actions` en su retorno; el merge de LangGraph conserva el valor de `actions` ya escrito por `extract_actions`.

**Rationale**: Flujo lineal; mock_result sigue proporcionando minutes y executive_summary. Actions proviene exclusivamente de la extracción real.

---

## 7. Variantes lingüísticas y edge cases (instrucciones en prompt)

**Decisión**: El prompt incluye explícitamente:
- Variantes: "se encargará", "debe", "comprometió a", "acordó que", etc.
- Varios responsables → primer nombre mencionado.
- Responsable por cargo sin nombre → "Por asignar".
- Acciones redundantes → consolidar, preferir variante más específica.
- Evitar "|" y ";" en acción y responsable.

**Rationale**: El LLM maneja bien estas reglas semánticas cuando están explícitas en el prompt.
