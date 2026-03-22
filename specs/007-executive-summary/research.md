# Research: Ver resumen ejecutivo

**Feature**: 007-executive-summary | **Date**: 2026-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001-006), la Constitución, la spec clarificada y el patrón establecido por generate_minutes. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Generación con LLM vs plantillas estáticas

**Decisión**: Usar LLM para generar el resumen ejecutivo a partir de participantes, temas, acciones y minuta.

**Rationale**: La spec exige síntesis que destaque "decisiones tomadas, acciones críticas, conclusiones principales" de forma natural. Las plantillas fijas no permiten priorización dinámica ni adaptación al contenido. Un LLM con prompt especializado puede producir un resumen ultra-conciso y accionable.

**Alternativas consideradas**:
- Plantilla fija: No cumple "síntesis clara y accionable"; rechazada.
- Extracción por regex/reglas: Insuficiente para síntesis semántica; rechazada.

---

## 2. Retry si el LLM excede 30 palabras (clarificación de la spec)

**Decisión**: Si el modelo devuelve más de 30 palabras (conteo: split por espacios), re-invocar con un prompt ajustado que enfatice "máximo 30 palabras, acorta el texto anterior" hasta cumplir el límite. Límite de reintentos: 2 (máximo 3 llamadas al LLM) para evitar bucles infinitos; si tras 3 intentos sigue excediendo, truncar en palabra 30 como fallback.

**Rationale**: La spec aclara explícitamente "re-pedir al modelo que acorte (retry con prompt ajustado)". Prioriza coherencia sobre truncado brusco. El fallback garantiza que nunca se devuelva >30 palabras.

**Alternativas consideradas**:
- Solo truncar: Menor calidad; la spec rechazó truncado como estrategia principal.
- Sin límite de reintentos: Riesgo de bucle; límite 2 reintentos es razonable.

---

## 3. Caso sin datos (participantes, temas y acciones vacíos)

**Decisión**: Misma regla que generate_minutes. Si `participants`, `topics` y `actions` están vacíos o equivalen a valores "sin datos", el nodo retorna `executive_summary: "Resumen: No se identificó información procesable en la reunión."` sin invocar el LLM.

**Rationale**: Clarificación de la spec; alineado con 006-generate-minutes. Evita llamada al LLM cuando no hay contenido que resumir.

**Regla de detección**: Igual que generate_minutes: considerar vacío si las tres fuentes están vacías o contienen únicamente los literales de "sin datos" (ej. "No identificados", "No hay temas identificados", "No hay acciones identificadas").

---

## 4. Integración en el grafo

**Decisión**: Insertar `create_summary` entre `generate_minutes` y `mock_result`. `mock_result` deja de incluir `executive_summary` en su retorno; el merge de LangGraph conserva el valor ya escrito por `create_summary`.

**Rationale**: El resumen depende de toda la información procesada, incluida la minuta. Debe ejecutarse después de generate_minutes. Patrón idéntico al de generate_minutes con mock_result.

---

## 5. Idioma y contenido (instrucciones en prompt)

**Decisión**: El prompt instruye explícitamente: resumen en español, máximo 30 palabras (split por espacios), enfocado en decisiones tomadas, acciones críticas y conclusiones principales. Síntesis clara y accionable. Para reuniones informativas: temas principales, tono profesional.

**Rationale**: La spec lo exige; las instrucciones explícitas reducen variabilidad del LLM.

---

## 6. UI: Botón Procesar desactivado hasta Limpiar

**Decisión**: En Gradio, el handler de `process_btn.click` debe devolver `gr.update(interactive=False)` para el botón Procesar como output adicional. Así el botón se desactiva inmediatamente al hacer clic (antes de que termine el procesamiento). El botón permanece desactivado hasta que el usuario haga clic en Limpiar. Tras Limpiar, `do_clear` vacía todo; cuando el usuario vuelva a introducir texto o cargar archivo, `update_inputs` (en change de text_input y file_input) reactivará el botón.

**Rationale**: FR-005, FR-006, FR-007. Gradio no tiene estado "post-proceso" nativo; la desactivación se logra devolviendo `interactive=False` en la respuesta del click. La reactivación depende del flujo existente: Limpiar → campos vacíos → process_btn=False; usuario añade contenido → change event → process_btn=True.
