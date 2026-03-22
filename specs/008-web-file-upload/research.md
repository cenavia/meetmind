# Research: Subir archivos desde la interfaz web

**Feature**: 008-web-file-upload | **Date**: 2026-03-22

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan de la spec clarificada, la Constitución, el stack existente (Gradio, httpx) y el plan de 007-executive-summary. Este documento consolida las elecciones de diseño.

---

## 1. Validación de archivos en el cliente (Gradio)

**Decisión**: Validar extensión y tamaño en la UI antes de enviar a la API. Usar `file_types` de `gr.File` para restringir formatos; añadir validación en Python del tamaño (500 MB) y extensión permitida por si el usuario manipula el cliente.

**Rationale**: FR-005 exige validar antes de enviar. Gradio permite `file_types` (lista de extensiones); la validación de tamaño debe hacerse al leer el archivo (Path.stat().st_size). Validar por extensión es suficiente para UX; la API puede re-validar MIME.

**Alternativas consideradas**:
- Solo validar en la API: peor UX (el usuario envía y espera para recibir error).
- Validar MIME en cliente: complejidad añadida; la extensión es un proxy razonable para formatos conocidos.

---

## 2. Timeout de 10 minutos (httpx)

**Decisión**: Configurar `timeout=600.0` (10 minutos) en las llamadas httpx a la API para procesamiento de archivos. Mantener timeout menor (30 s) para process/text si se desea, o unificar en 600 s.

**Rationale**: La spec clarifica timeout de 10 minutos. httpx acepta `timeout` en segundos. 600 s = 10 min. Si el servicio no responde en 10 min, httpx lanza TimeoutException; la UI debe capturarla y mostrar mensaje amigable (FR-006).

**Alternativas consideradas**:
- Timeout menor: no cumple la spec.
- Streaming/progress: Gradio no expone fácilmente progress de requests HTTP; `show_progress=True` muestra spinner genérico, suficiente para la spec.

---

## 3. Integración API actual vs multimedia

**Decisión**: La UI acepta y valida todos los formatos especificados (MP4, MOV, MP3, WAV, M4A, TXT, MD). Si la API actual solo soporta TXT/MD (según `process.py`), los archivos multimedia serán rechazados por la API con 415 u otro código; la UI mostrará el mensaje de error amigable devuelto. Cuando US-010 extienda la API a multimedia, la UI funcionará sin cambios adicionales.

**Rationale**: La spec exige la lista completa. Implementar validación completa en la UI evita rework futuro. La API es la fuente de verdad; si no soporta un formato, devuelve error y la UI lo presenta al usuario.

**Nota**: Si se desea una UX más proactiva, la UI podría deshabilitar temporalmente multimedia hasta que la API lo soporte; eso añade complejidad de configuración. Se opta por validar y enviar; el error de la API es mensaje suficiente.

---

## 4. Layout y secciones de resultados

**Decisión**: Mantener el formato actual (Markdown con secciones ## Participantes, ## Temas, etc.) que ya cumple FR-004. Si se desea tabs o collapsibles, Gradio ofrece `gr.Tabs` y `gr.Accordion`; para MVP el Markdown estructurado es suficiente y ya está implementado.

**Rationale**: La spec dice "tabs o colapsables"; el formato actual es una sección clara. SC-004 exige localización en <10 s; el Markdown con encabezados lo permite. Una mejora futura sería migrar a Accordion para cada sección.

---

## 5. Configuración de URL (FR-008)

**Decisión**: Usar `API_BASE_URL` (variable de entorno) ya existente en `config.py`. Añadir opcionalmente un campo de configuración en la UI (ej. `gr.Textbox` colapsado o en configuración avanzada) si la spec exige "input de configuración". La spec dice "variable de entorno o input"; `API_BASE_URL` cumple la primera parte. Para Pablo en local, configurar la variable es suficiente.

**Rationale**: Ya existe `get_api_base_url()` que lee `API_BASE_URL`. No añadir input de URL en la UI por defecto para mantener la interfaz simple; documentar la variable en quickstart. Si se requiere input explícito, se añade un campo opcional en una iteración posterior.

---

## 6. Botón Procesar deshabilitado sin archivo (clarificación)

**Decisión**: El flujo actual ya tiene `update_inputs` que habilita `process_btn` cuando hay texto O archivo. Para cumplir "Procesar deshabilitado sin archivo" en el modo archivo: cuando solo hay file_input (sin texto), el botón se habilita solo si hay archivo válido. El flujo actual `can_process = has_t or has_f` ya lo hace: sin archivo y sin texto, `can_process=False`. Tras validar, si el archivo es inválido (formato/tamaño), no se debe habilitar el envío. La validación en `process_dispatch` rechaza antes de enviar; el botón puede estar habilitado si hay archivo seleccionado (aunque sea inválido), y al pulsar se muestra el error. Alternativamente, validar en `update_inputs` y no habilitar si el archivo es inválido. Para simplicidad: habilitar cuando hay archivo O texto; la validación al procesar muestra el error. La clarificación dice "deshabilitado hasta que haya archivo" — en el modo texto, el botón se habilita con texto. En el modo archivo, se habilita cuando hay archivo. Correcto.

**Rationale**: El comportamiento actual es correcto. Sin contenido (ni texto ni archivo), el botón está deshabilitado. Con archivo o texto, habilitado. La validación de formato/tamaño ocurre al procesar; si falla, mensaje amigable.
