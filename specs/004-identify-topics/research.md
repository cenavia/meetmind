# Research: Ver temas principales discutidos

**Feature**: 004-identify-topics | **Date**: 2026-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001/002/003), la Constitución y la spec clarificada. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Extracción con LLM vs heurística (keywords, clustering)

**Decisión**: Usar LLM con salida estructurada (Pydantic) para identificar temas.

**Rationale**: Los temas en contexto de reunión requieren comprensión semántica (granularidad apropiada, evitar genéricos, consolidar variantes). Las reglas de la spec (3-5 temas, consolidar solapados, preferir variante específica, orden por primera aparición) no se resuelven bien con keywords ni clustering. Un LLM con prompt especializado ofrece el mejor balance.

**Alternativas consideradas**:
- TF-IDF o RAKE para extracción de keywords: No captura semántica; difícil evitar genéricos ("reunión", "discusión"). Rechazada.
- Clustering de embeddings: Más complejo de integrar; orden por primera aparición requiere post-proceso adicional. Rechazada para MVP.

---

## 2. Structured output con Pydantic

**Decisión**: Definir un modelo Pydantic (ej. `TopicsExtraction`) con campo `topics: list[str]` para que el LLM devuelva entre 1 y 5 temas. Post-procesar en el nodo: ordenar por primera aparición en raw_text, formatear como string separado por punto y coma, devolver "No hay temas identificados" si lista vacía.

**Rationale**: LangChain/LangGraph soportan `with_structured_output()` con Pydantic. La consolidación de temas solapados y la granularidad se instruyen en el prompt; el nodo aplica orden por primera aparición recorriendo el texto original (igual que extract_participants).

**Alternativas consideradas**:
- JSON schema sin Pydantic: Funcional pero Pydantic integra mejor con LangChain.
- Salida en texto libre: Requiere parsing frágil; rechazada.

---

## 3. Orden por primera aparición

**Decisión**: El prompt instruye al LLM a devolver temas; el nodo post-procesa para ordenar por primera aparición en `raw_text` (usando `str.find()` o similar para cada tema).

**Rationale**: La spec exige orden de primera aparición. El LLM puede no respetar orden; es más robusto aplicar la regla en código (mismo patrón que extract_participants).

---

## 4. Consolidación de temas solapados

**Decisión**: Instruir en el prompt que cuando haya temas solapados (ej. "Presupuesto" y "Presupuesto Q2"), debe consolidarse en uno solo prefiriendo la variante más específica. El nodo no aplica lógica adicional; confiar en el LLM para la consolidación semántica.

**Rationale**: La consolidación es semántica (saber que "Presupuesto" y "Presupuesto Q2" son el mismo concepto). Un LLM lo resuelve bien; implementar lógica de similitud en código sería más frágil.

**Alternativas consideradas**:
- Post-proceso con similitud de strings (Levenshtein, embeddings): Más complejo; el prompt es suficiente para MVP.

---

## 5. Caso "No hay temas identificados"

**Decisión**: Si el LLM devuelve lista vacía o el texto es muy corto/vacío, el nodo retorna `topics: "No hay temas identificados"` (nunca cadena vacía).

**Rationale**: Clarificación 1 de la spec: siempre texto explícito cuando 0 temas.

---

## 6. Loader y manejo de errores en UI

**Decisión**: La UI actual usa `show_progress=True` en `process_btn.click()`, que muestra indicador de carga de Gradio durante la llamada a la API. Cuando la API falla, la función retorna mensaje de error y el loader se oculta automáticamente. Verificar que el loader sea visible; si no, ajustar según skill gradio (ej. `gr.Loader`, componente de carga explícito).

**Rationale**: La spec exige loader visible durante procesamiento y ocultarlo mostrando error si falla. El flujo actual de Gradio con show_progress y manejo de excepciones cumple el comportamiento; si la visibilidad es insuficiente, añadir componente dedicado.

---

## 7. Integración en el grafo

**Decisión**: Insertar `identify_topics` entre `extract_participants` y `mock_result`. `mock_result` deja de incluir `topics` en su retorno; el merge de LangGraph conserva el valor de `topics` ya escrito por `identify_topics`.

**Rationale**: Flujo lineal; mock_result sigue proporcionando actions, minutes, executive_summary. Topics proviene exclusivamente de la extracción real.
