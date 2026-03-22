# Contract: Validación de archivos multimedia

**Feature**: 009-multimedia-recording | **Aplica a**: `POST /api/v1/process/file`

---

## Formatos soportados

| Categoría | Extensiones | MIME (referencia) |
|-----------|-------------|-------------------|
| Audio | .mp3, .wav, .m4a | audio/mpeg, audio/wav, audio/x-wav, audio/mp4 |
| Video | .mp4, .mov, .webm, .mkv | video/mp4, video/quicktime, video/webm, video/x-matroska |

Validación por extensión (case-insensitive). Si Content-Type es application/octet-stream, confiar en extensión si está en la lista.

---

## Límites

| Parámetro | Valor por defecto | Configurable |
|-----------|-------------------|--------------|
| Tamaño máximo | 500 MB | `MAX_FILE_SIZE_MB` (env) |

---

## Respuestas de error

| Condición | Código | Mensaje (español) |
|-----------|--------|-------------------|
| Extensión no permitida | 415 | "Formato no soportado. Formatos permitidos: MP4, MOV, MP3, WAV, M4A, WEBM, MKV." |
| Archivo > 500 MB | 400 | "El archivo supera el límite de 500 MB." |
| Archivo vacío | 422 | "El archivo está vacío." |
| Error lectura | 500 | "Error al leer el archivo. Intenta de nuevo." |

---

## Texto (TXT, MD)

Los formatos de texto existentes (.txt, .md) siguen soportados. La validación de texto se delega en `file_loader.py`. No aplicar límite de 500 MB a texto (el límite actual de caracteres se mantiene).
