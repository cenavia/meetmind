# Research: Procesar notas en texto

**Feature**: 002-text-notes-processing | **Date**: 2025-03-21

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan del stack existente (001) y de la spec clarificada. Este documento consolida las elecciones de diseño y alternativas consideradas.

---

## 1. Carga de archivos TXT/MD con encoding

**Decisión**: Leer con UTF-8 por defecto; si falla (UnicodeDecodeError), intentar latin-1; si ambos fallan, rechazar con mensaje claro.

**Rationale**: UTF-8 es estándar para español y Markdown. Latin-1 cubre archivos legacy europeos. Evita dependencias pesadas (chardet) en esta fase.

**Alternativas consideradas**:
- chardet: Detección automática de encoding. Rechazada para MVP: añade dependencia y latencia; UTF-8 + latin-1 cubre el 99% de casos.
- Solo UTF-8: Rechazada; muchos archivos Windows antiguos usan latin-1/cp1252.

---

## 2. Endpoint API: texto vs archivo

**Decisión**: Dos endpoints separados: `POST /process/text` (existente) y `POST /process/file` (nuevo).

**Rationale**: Contratos claros, validación independiente, tipado fuerte. La UI conoce el modo (texto o archivo) y llama al endpoint correcto.

**Alternativas consideradas**:
- Endpoint único que acepta `application/json` o `multipart/form-data`: Más complejo; content negotiation y validación condicional. Rechazada.
- Query param `?source=text|file`: Añade complejidad sin beneficio para el cliente.

---

## 3. Validación de formato (extensión y MIME)

**Decisión**: Validar extensión (.txt, .md) y MIME (text/plain, text/markdown). Rechazar si no coincide. Constitución exige validación MIME en uploads.

**Rationale**: Seguridad y UX. Evita procesar PDF, DOCX, etc. por error.

**Alternativas consideradas**:
- Solo extensión: Insuficiente; un PDF podría renombrarse a .txt.
- Solo contenido (magic bytes): Complejo para texto; MIME + extensión es suficiente.

---

## 4. UI Gradio: texto y archivo en misma pantalla

**Decisión**: `gr.Textbox` + `gr.File` en la misma fila/bloque. Lógica JS/Python para deshabilitar uno cuando el otro tiene contenido. `gr.File` con `file_types=[".txt", ".md"]`. `show_progress=True` en el handler; mensaje "Procesando..." durante la llamada a la API.

**Rationale**: Spec exige misma pantalla y bloqueo mutuo. Gradio `gr.File` devuelve ruta local; la UI lee el archivo y envía contenido o usa `files=` en httpx para multipart.

**Alternativas consideradas**:
- Subir archivo al servidor Gradio y que la UI envíe la ruta a la API: La API no tiene acceso al filesystem de Gradio; se debe enviar el contenido o el archivo en el request. Enviar archivo vía multipart es estándar.
- Dos pestañas: Spec rechazada (clarificación B: misma pantalla).

---

## 5. Límite de caracteres post-lectura

**Decisión**: Leer archivo completo en memoria, validar `len(contenido) <= 50_000`, rechazar con 400 si se excede.

**Rationale**: Alineado con 001 y spec. Validación tras lectura evita límite por bytes (UTF-8 variable).

**Alternativas consideradas**:
- Límite por bytes (ej. 200KB): Rechazada; spec exige límite por caracteres.
- Streaming: Innecesario para notas; archivos típicos <100KB.
