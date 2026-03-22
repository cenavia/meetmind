# Research: Ver minuta formal

**Feature**: 006-generate-minutes | **Date**: 2026-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001-005), la Constitución y la spec clarificada. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Generación con LLM vs plantillas estáticas

**Decisión**: Usar LLM para generar minuta narrativa a partir de participantes, temas y acciones.

**Rationale**: La spec exige "texto narrativo continuo" que integre la información de forma coherente. Las plantillas fijas no permiten variación natural ni adaptación al contenido. Un LLM con prompt especializado puede producir prosa profesional que fluya y priorice la información disponible.

**Alternativas consideradas**:
- Plantilla fija (ej. "Reunión con {participants}. Temas: {topics}. Acciones: {actions}"): No cumple "texto narrativo continuo" ni "tono profesional"; rechazada.
- Reglas de concatenación: Resultaría en listas o bloques, no narrativa fluida; rechazada.

---

## 2. Salida en texto libre vs structured output

**Decisión**: Invocar el LLM con salida en texto libre (no Pydantic). Post-procesar para truncar si excede 150 palabras.

**Rationale**: La minuta es prosa libre; no hay campos estructurados que validar. Usar `invoke()` sin `with_structured_output()` simplifica el flujo. El único requisito (≤150 palabras) se garantiza con post-procesamiento.

**Alternativas consideradas**:
- Pydantic con un único campo `minutes: str`: Funcional pero redundante; el LLM ya devuelve string; rechazada por simplicidad.
- JSON con clave "minutes": Añade parsing innecesario; rechazada.

---

## 3. Truncamiento post-proceso cuando el LLM excede 150 palabras

**Decisión**: Tras obtener el texto del LLM, contar palabras (split por espacios). Si >150, truncar en el último límite de palabra que preserve oraciones completas (o, como fallback, en la palabra 150).

**Rationale**: La spec permite "truncamiento o condensación preservando coherencia". Cortar en un límite de oración evita frases a medias. Si no hay punto/coma cercano, cortar en palabra 150.

**Alternativas consideradas**:
- Re-prompt al LLM para acortar: Más latencia y coste; rechazada.
- Solo instruir en el prompt: El LLM puede exceder; post-proceso es fallback obligatorio; aceptada.

---

## 4. Caso sin datos (participantes, temas y acciones vacíos)

**Decisión**: Si `participants`, `topics` y `actions` están vacíos o equivalen a valores "sin datos" (ej. "No identificados", "No hay temas identificados", "No hay acciones identificadas"), el nodo retorna `minutes: "Minuta: No se identificó información procesable en la reunión."` sin invocar el LLM.

**Rationale**: Clarificación de la spec: mensaje fijo estándar breve; nunca cadena vacía. Evitar llamada al LLM cuando no hay contenido que resumir ahorra latencia y coste.

**Regla de detección**: Considerar "vacío" si las tres fuentes están vacías o contienen únicamente los literales de "sin datos" de los nodos previos (e.g. "No identificados", "No hay temas identificados", "No hay acciones identificadas").

---

## 5. Integración en el grafo

**Decisión**: Insertar `generate_minutes` entre `extract_actions` y `mock_result`. `mock_result` deja de incluir `minutes` en su retorno; el merge de LangGraph conserva el valor ya escrito por `generate_minutes`.

**Rationale**: Patrón idéntico a extract_actions para actions. El flujo queda: extract_actions → generate_minutes → mock_result. mock_result solo proporciona executive_summary (placeholder hasta US-007).

---

## 6. Idioma y tono (instrucciones en prompt)

**Decisión**: El prompt instruye explícitamente: minuta en español, tono profesional y formal, texto narrativo continuo (sin secciones con encabezados), máximo 150 palabras, integrar participantes, temas y acciones de forma coherente.

**Rationale**: La spec lo exige; las instrucciones explícitas reducen variabilidad del LLM.
