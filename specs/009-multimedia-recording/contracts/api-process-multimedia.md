# Contract: API procesamiento de archivos (multimedia y texto)

**Feature**: 009-multimedia-recording | **Aplica a**: `POST /api/v1/process/file`

---

## Extensión del endpoint existente

El endpoint `POST /api/v1/process/file` extiende su soporte de solo texto (TXT, MD) a:

- **Texto**: TXT, MD (comportamiento actual)
- **Multimedia**: MP4, MOV, MP3, WAV, M4A, WEBM, MKV

---

## Request

| Método | Ruta | Content-Type |
|--------|------|--------------|
| POST | /api/v1/process/file | multipart/form-data |

Campo: `file` (UploadFile)

---

## Respuesta exitosa (200 OK)

```json
{
  "participants": "string",
  "topics": "string",
  "actions": "string",
  "minutes": "string",
  "executive_summary": "string"
}
```

Mismo esquema que `process/text`. Sin cambios en la estructura.

---

## Timeout

- **Procesamiento síncrono**: hasta 15 minutos (900 segundos).
- Configurable: `PROCESSING_TIMEOUT_SEC` (env).
- Si se supera: HTTP 408 con mensaje amigable en español.

---

## Errores (todos en español)

| Código | Condición | detail |
|--------|-----------|--------|
| 400 | Archivo > 500 MB | "El archivo supera el límite de 500 MB." |
| 415 | Formato no soportado | "Formato no soportado. Formatos permitidos: MP4, MOV, MP3, WAV, M4A, WEBM, MKV." |
| 422 | Archivo vacío, texto vacío | Mensaje específico |
| 408 | Timeout > 15 min | "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde." |
| 422 | Codec no soportado, archivo corrupto | "El formato del archivo no es compatible." o "No se pudo procesar el archivo." |
| 500 | Error interno | Mensaje genérico; no exponer stack trace |

---

## Flujo

1. Validar extensión y tamaño.
2. Leer contenido del archivo.
3. Si multimedia: transcribir → raw_text.
4. Si texto: load_text_file → raw_text.
5. graph.invoke({"raw_text": raw_text}).
6. Retornar ProcessMeetingResponse.

---

## Compatibilidad con 008-web-file-upload

La UI (008) envía archivos con timeout de 10 min. La API tiene timeout de 15 min. Si la UI usa 10 min, el cliente verá timeout antes que la API. Recomendación: alinear timeout UI con API (15 min) cuando 009 esté activo, o mantener 10 min en UI si se prioriza feedback rápido (el usuario verá "tardó demasiado" a los 10 min).
