# Research: Ver extracción de participantes

**Feature**: 003-participants-extraction | **Date**: 2025-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001/002), la Constitución y la spec clarificada. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Extracción con LLM vs heurística (NER / regex)

**Decisión**: Usar LLM con salida estructurada (Pydantic) para extraer participantes.

**Rationale**: Los nombres en contexto de reunión son ambiguos ("Juan" vs "Juan Pérez", "el Dr. García"). Un NER genérico no entiende el dominio; las reglas de la spec (excluir genéricos, deduplicar, preferir nombre completo, excluir títulos) requieren comprensión semántica. Un LLM con prompt especializado y structured output ofrece el mejor balance calidad/efectividad.

**Alternativas consideradas**:
- spaCy NER o similar: No captura bien el contexto "reunión"; requiere post-procesamiento extenso para dedup y variantes. Rechazada para MVP.
- Regex + diccionario de stopwords: Frágil ante variaciones; no resuelve deduplicación semántica. Rechazada.

---

## 2. Structured output con Pydantic

**Decisión**: Definir un modelo Pydantic (ej. `ParticipantsExtraction`) con campo `participants: list[str]` para que el LLM devuelva una lista de nombres. Post-procesar en el nodo: ordenar por primera aparición, formatear como string separado por comas.

**Rationale**: LangChain/LangGraph soportan `with_structured_output()` con Pydantic. Garantiza formato válido y evita parsing manual de texto libre. La deduplicación y preferencia por nombre completo pueden instruirse en el prompt; el nodo aplica orden por primera aparición recorriendo el texto original.

**Alternativas consideradas**:
- JSON schema sin Pydantic: Funcional pero Pydantic integra mejor con el ecosistema LangChain.
- Salida en texto libre: Requiere parsing frágil; rechazada.

---

## 3. Orden por primera aparición

**Decisión**: El prompt instruye al LLM a devolver nombres; el nodo post-procesa para ordenar por primera aparición en `raw_text` (usando `str.find()` o similar para cada nombre).

**Rationale**: La spec exige orden de primera aparición. El LLM puede no respetar orden; es más robusto aplicar la regla en código.

**Alternativas consideradas**:
- Confiar en que el LLM ordene: Inconsistente; rechazada.
- Orden alfabético: Contradice la spec (clarificación 3: orden de primera aparición).

---

## 4. Caso "No identificados"

**Decisión**: Si el LLM devuelve lista vacía o el texto es muy corto/vacío, el nodo retorna `participants: "No identificados"` (nunca cadena vacía).

**Rationale**: Clarificación 1 de la spec: siempre "No identificados" cuando no hay participantes.

---

## 5. Integración en el grafo

**Decisión**: Insertar `extract_participants` entre `preprocess` y `mock_result`. `mock_result` deja de incluir `participants` en su retorno; el merge de LangGraph conserva el valor de `participants` ya escrito por `extract_participants`.

**Rationale**: Flujo lineal; mock_result sigue proporcionando topics, actions, minutes, executive_summary. Participants proviene exclusivamente de la extracción real.

---

## 6. LLM y configuración

**Decisión**: Usar el LLM configurado en el proyecto (ChatOpenAI u otro proveedor según variables de entorno). La Constitución exige API keys por variables de entorno; no hardcodear credenciales.

**Rationale**: Alineado con 001/002; el nodo invoca el LLM estándar del proyecto.
