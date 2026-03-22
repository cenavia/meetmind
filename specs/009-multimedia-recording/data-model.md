# Data Model: Procesar grabación multimedia

**Feature**: 009-multimedia-recording | **Date**: 2026-03-22

## Entidades

### Archivo multimedia (entrada)

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| extensiones | set | .mp4, .mov, .mp3, .wav, .m4a, .webm, .mkv | Extensiones permitidas (case-insensitive) |
| MIME permitidos | set | audio/mpeg, audio/wav, audio/mp4, video/mp4, video/quicktime, video/webm, video/x-matroska, etc. | Content-Type aceptados |
| tamaño_máximo_bytes | int | 500 * 1024 * 1024 (500 MB) | Configurable vía MAX_FILE_SIZE_MB |
| contenido | bytes | En memoria durante procesamiento | No se persiste (Out of Scope) |

**Reglas de validación**:
- Extensión: debe estar en la lista permitida.
- Tamaño: `len(content) <= MAX_FILE_SIZE_MB * 1024 * 1024`.
- MIME: si presente, debe ser compatible con la extensión; si application/octet-stream, confiar en extensión.
- Si no cumple: HTTP 400/415 con mensaje en español.

### Transcripción

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| texto | str | Texto transcrito del audio |
| idioma_detectado | str | (opcional) Idioma detectado por Whisper |
| duración_segundos | float | (opcional) Duración del audio para métricas |

**Ciclo de vida**: Generada en memoria; pasa a `raw_text` del MeetingState; no se persiste.

### Resultados de procesamiento

Sin cambios respecto al esquema existente. La API devuelve el mismo `ProcessMeetingResponse`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| participants | str | Nombres separados por coma |
| topics | str | Temas |
| actions | str | Acciones |
| minutes | str | Minuta |
| executive_summary | str | Resumen ≤30 palabras |

### Estado de procesamiento

| Estado | Descripción |
|--------|-------------|
| validando | Validación de archivo (tipo, tamaño) |
| transcribiendo | Transcripción en curso (solo multimedia) |
| procesando | Workflow LangGraph en ejecución |
| completado | Resultados listos |
| error | Fallo (archivo corrupto, codec no soportado, timeout, transcripción fallida) |
| async_pendiente | (futuro) Job creado; usuario consulta más tarde |

### Job asíncrono (futuro / FR-010)

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| job_id | str | UUID o identificador único |
| estado | enum | pending, processing, completed, failed |
| resultado | ProcessMeetingResponse | (cuando completed) |
| error | str | (cuando failed) Mensaje amigable |
| creado_en | datetime | Timestamp |
| completado_en | datetime | (opcional) |

**Nota**: Para MVP, el flujo async puede no implementarse; el timeout devuelve HTTP 408 con mensaje. Si se implementa, requiere almacén (DB o Redis).

## Flujo de datos

```
API recibe UploadFile (multimedia o texto)
        ↓
¿Extensión en lista? → No → HTTP 415, mensaje formatos permitidos
        ↓ Sí
¿Tamaño ≤ 500 MB? → No → HTTP 400, mensaje límite
        ↓ Sí
¿Es multimedia? (por extensión/MIME)
        ↓ Sí                    ↓ No (TXT/MD)
Transcribir (Whisper)           load_text_file
        ↓                           ↓
¿Timeout 15 min? → Sí → (futuro: crear job, 202; MVP: 408)
        ↓ No
raw_text = transcripción
        ↓
graph.invoke({"raw_text": raw_text})
        ↓
ProcessMeetingResponse
```

## Validaciones por capa

| Capa | Validación |
|------|------------|
| API (process_file) | Extensión en [.mp4, .mov, .mp3, .wav, .m4a, .webm, .mkv] o [.txt, .md] |
| API | Tamaño ≤ 500 MB (configurable) |
| API | MIME compatible (si presente) |
| Servicio transcripción | Extracción de audio (video) → transcripción; capturar errores de codec |
| API (errores) | Mensajes en español; no exponer stack traces |
