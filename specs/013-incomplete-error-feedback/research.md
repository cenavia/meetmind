# Research: 013-incomplete-error-feedback

**Date**: 2026-03-22

## 1. Forma de `processing_errors`: string vs lista

**Decision**: Usar **`list[str]`** en el estado del grafo (`MeetingState`) y en los **modelos Pydantic de respuesta** (`ProcessMeetingResponse`, `MeetingRecordResponse`). En **BD**, mantener columna `Text` y serializar como **JSON array** (UTF-8) para preservar ítems múltiples sin ambigüedad de separadores; al leer registros antiguos con texto plano legacy, tratar como un único elemento o migración puntual en código de lectura.

**Rationale**: Cumple FR-002 y contrato spec; evita parsing frágil por newlines en mensajes multilínea.

**Alternatives considered**: Solo newline-separated en columna (simple pero frágil si el mensaje contiene saltos de línea); columna JSON nativa (SQLite 3.38+ JSON o tipo dedicado) — posible evolución si el volumen o consultas lo exigen.

## 2. Reducer de estado LangGraph para errores

**Decision**: Si varios nodos aportan advertencias en la misma invocación, usar **`Annotated[list[str], operator.add]`** (o patrón equivalente documentado en `langgraph-fundamentals`) en el campo de estado para **concatenar** listas devueltas por nodos.

**Rationale**: Evita que el último nodo pise advertencias previas.

**Alternatives considered**: Un solo nodo agrega al final del flujo (rechazado: pierde avisos de preprocess/transcripción temprana).

## 3. Derivación de `status` para respuesta HTTP inmediata

**Decision**: Tras `graph.invoke`, calcular `status` con la **misma lógica** que `status_from_graph_result` (completar con ramas **`failed`** cuando el grafo o la API abortan antes de resultado útil). Incluir **`status`** explícito en `ProcessMeetingResponse` además de persistirlo en `MeetingRecord`.

**Rationale**: FR-001 y UI necesitan etiqueta sin inferir solo desde presencia de errores; hoy el POST 200 no expone `status` ni lista de errores en el cuerpo.

**Alternatives considered**: Inferir solo en cliente (rechazado: incumple FR-013).

## 4. Umbral “texto muy corto” (20 palabras)

**Decision**: Implementar en **`preprocess_node`**: `len(raw.split()) < 20` tras `strip()` → añadir mensaje fijo en español a `processing_errors` (configurable vía constante o `src/config` si se desea N distinto).

**Rationale**: Alineado con aclaración de spec y BDD US-011.

**Alternatives considered**: Solo prefijo `[Información limitada]` en minuta (constitución IV) — se **mantiene como complemento** si los nodos downstream lo siguen generando; el umbral añade advertencia explícita en lista.

## 5. Transcripción copiable en Gradio

**Decision**: Añadir `gr.Textbox` (o equivalente según versión) **solo lectura** con **`buttons` que incluyan copiar** si la API/SSE entrega `transcript` (o nombre acordado en contrato); ocultar o vaciar cuando `transcription_backend == "none"` y no hay texto transcrito.

**Rationale**: Cumple FR-008 y US-011; depende de exponer el campo en el evento final del stream o en JSON síncrono.

**Alternatives considered**: Solo Markdown con botón copiar si la versión de Gradio lo soporta de forma uniforme — valorar en implementación según `gradio` skill.

## 6. Manejo global de excepciones FastAPI

**Decision**: Registrar handlers para **`HTTPException`** (sin cambiar detalles ya españoles) y **`Exception`** no capturada que devuelva **`detail` genérico en español** y registre stack solo en logs (constitución seguridad).

**Rationale**: FR-003 / FR-013.

**Alternatives considered**: Solo try/except por endpoint (rechazado: duplicación y fugas en rutas olvidadas).

## 7. “Detalles técnicos” en UI

**Decision**: Contenido estático seguro: p. ej. etiqueta de backend de transcripción (`cloud`/`local`/`none`), timeout configurado en minutos — **sin** variables de entorno con secretos, sin rutas absolutas del servidor.

**Rationale**: FR-007 + aclaración sesión (cualquier usuaria puede expandir).

**Alternatives considered**: Ocultar en producción (rechazado por aclaración A).
