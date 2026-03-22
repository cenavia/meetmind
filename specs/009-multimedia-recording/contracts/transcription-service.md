# Contract: Servicio de transcripción

**Feature**: 009-multimedia-recording | **Aplica a**: `src/services/transcription.py`

---

## Interfaz

```python
def transcribe_audio(
    audio_path: str | Path,
    *,
    model: str = "base",
    language: str | None = None,
) -> str:
    """
    Transcribe un archivo de audio a texto.
    
    Args:
        audio_path: Ruta al archivo de audio (MP3, WAV, M4A) o video (se extrae audio).
        model: Modelo Whisper (tiny, base, small, medium, large).
        language: Código de idioma (ej. "es", "en") o None para autodetección.
    
    Returns:
        Texto transcrito.
    
    Raises:
        TranscriptionError: Si el archivo no puede procesarse (codec no soportado, corrupto).
    """
```

---

## Flujo interno

1. Si el archivo es video (por extensión): extraer pista de audio a archivo temporal WAV con ffmpeg.
2. Cargar modelo Whisper (cachear para evitar recargas).
3. Transcribir con `whisper.transcribe()`.
4. Retornar `result["text"]`.
5. Eliminar archivos temporales.

---

## Manejo de errores

| Condición | Acción |
|-----------|--------|
| ffmpeg no instalado | Lanzar TranscriptionError con mensaje "El sistema no puede procesar archivos de video. Contacta al administrador." |
| Codec no soportado | TranscriptionError: "El formato del archivo no es compatible." |
| Archivo corrupto | TranscriptionError: "No se pudo procesar el archivo. Verifica que no esté dañado." |
| Transcripción vacía | Retornar "" (el grafo manejará texto vacío según robustez) |

Todos los mensajes en español. No exponer excepciones crudas (RuntimeError, etc.) al usuario.

---

## Configuración

| Variable | Default | Descripción |
|----------|---------|-------------|
| TRANSCRIPTION_MODEL | small | Modelo Whisper (tiny … large-v3); `small` por defecto para reuniones |
| TRANSCRIPTION_LANGUAGE | es | Idioma (es, en, …); vacío = autodetección |
| WHISPER_DEVICE | auto | auto / cuda / cpu / mps |
