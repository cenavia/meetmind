# Data Model: Subir archivos desde la interfaz web

**Feature**: 008-web-file-upload | **Date**: 2026-03-22

## Entidades

### Archivo subido

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| formatos | set | MP4, MOV, MP3, WAV, M4A, TXT, MD | Extensiones permitidas (case-insensitive) |
| tamaño_máximo_bytes | int | 500 * 1024 * 1024 (500 MB) | Rechazar antes de enviar si excede |
| MIME (opcional) | str | Validación en API | La UI valida por extensión; la API puede validar MIME |

**Reglas de validación**:
- Extensión: debe estar en la lista permitida (.mp4, .mov, .mp3, .wav, .m4a, .txt, .md).
- Tamaño: `Path(file).stat().st_size <= 500 * 1024 * 1024`.
- Si no cumple: no enviar; mostrar mensaje en español indicando formato/tamaño permitido.

### Resultados de procesamiento (respuesta de la API)

La UI consume la respuesta de `POST /api/v1/process/file` o `POST /api/v1/process/text`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| participants | str | Nombres separados por coma |
| topics | str | Temas; separador según PRD |
| actions | str | Acciones; separador según PRD |
| minutes | str | Minuta generada |
| executive_summary | str | Resumen ≤30 palabras (007) |

La UI formatea estos campos como Markdown en secciones (## Participantes, ## Temas, etc.).

### Estado de UI

| Estado | process_btn.interactive | file_input | Descripción |
|--------|-------------------------|------------|-------------|
| Sin contenido (texto y archivo vacíos) | False | - | No se puede procesar |
| Con archivo o texto | True | - | Usuario puede procesar |
| Tras clic en Procesar (inmediato) | False | - | Se desactiva al instante (007) |
| Post-procesamiento | False | - | Permanece desactivado hasta Limpiar |
| Tras clic en Limpiar | False | vacío | Usuario puede cargar de nuevo |

### Mensajes de error (español)

| Escenario | Mensaje tipo |
|-----------|--------------|
| Archivo no soportado | "Formato no soportado. Formatos permitidos: multimedia (MP4, MOV, MP3, WAV, M4A), texto (TXT, MD)." |
| Archivo >500 MB | "El archivo supera el límite de 500 MB." |
| Timeout (10 min) | "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto." |
| Error de conexión | "No se puede conectar con la API. Verifica que esté ejecutándose." |
| Error HTTP (4xx/5xx) | Mensaje amigable derivado del detail de la API; sin stack traces |

## Flujo de datos

```
Usuario selecciona archivo
        ↓
¿Extensión en lista permitida? → No → Mensaje error formato; no enviar
        ↓ Sí
¿Tamaño ≤ 500 MB? → No → Mensaje error tamaño; no enviar
        ↓ Sí
POST /api/v1/process/file (timeout 10 min)
        ↓
¿Timeout? → Sí → Mensaje error timeout
        ↓ No
¿HTTP 2xx? → No → Mensaje amigable del detail (sin detalles técnicos)
        ↓ Sí
Formatear JSON → Markdown → Mostrar en output
        ↓
Procesar desactivado hasta Limpiar
```

## Validaciones por capa

| Capa | Validación |
|------|------------|
| UI (antes de enviar) | Extensión en [.mp4, .mov, .mp3, .wav, .m4a, .txt, .md] |
| UI (antes de enviar) | Tamaño ≤ 500 MB |
| UI (errores) | Mensajes en español; no exponer stack traces ni códigos HTTP crudos |
| API | MIME, tamaño (si configurado); la UI hace pre-validación para mejor UX |
