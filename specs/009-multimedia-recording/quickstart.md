# Quickstart: Procesar grabación multimedia

**Feature**: 009-multimedia-recording | **Tiempo estimado**: 10 min (con ffmpeg y dependencias instaladas)

## Prerrequisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado
- **ffmpeg** instalado en el sistema (requerido por Whisper para audio/video)

### Instalar ffmpeg

```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Verificar
ffmpeg -version
```

## 1. Instalar dependencias

```bash
cd meetmind
uv sync --all-extras  # Incluye openai-whisper y pytest
```

**Nota**: `openai-whisper` ya está en pyproject.toml. Requiere ffmpeg instalado en el sistema.

## 2. Configuración (opcional)

| Variable | Default | Descripción |
|----------|---------|-------------|
| TRANSCRIPTION_MODEL | **small** | Modelo Whisper: tiny, base, small, medium, large, large-v2, large-v3. `small` equilibra calidad y tiempo para reuniones en español. |
| TRANSCRIPTION_LANGUAGE | **es** | Idioma ISO (ej. es, en). Vacío en `.env` = autodetección. |
| WHISPER_DEVICE | **auto** | `auto` elige CUDA / MPS (Apple Silicon) / CPU. Forzar `cpu` si hay errores en MPS. |
| MAX_FILE_SIZE_MB | 500 | Límite de tamaño de archivo en MB |
| PROCESSING_TIMEOUT_SEC | 900 | Timeout en segundos (15 min) |

```bash
# Opcional: más calidad (más lento y RAM)
# export TRANSCRIPTION_MODEL=medium
# Máxima calidad con GPU potente
# export TRANSCRIPTION_MODEL=large-v3
export MAX_FILE_SIZE_MB=500
```

## 3. Ejecutar la API

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Probar con archivo multimedia

### Con curl (MP3)

```bash
curl -X POST "http://localhost:8000/api/v1/process/file" \
  -H "accept: application/json" \
  -F "file=@reunion.mp3"
```

### Con curl (MP4)

```bash
curl -X POST "http://localhost:8000/api/v1/process/file" \
  -H "accept: application/json" \
  -F "file=@reunion.mp4"
```

### Respuesta esperada (200 OK)

```json
{
  "participants": "Marina, Pablo, ...",
  "topics": "Tema1; Tema2; ...",
  "actions": "Acción 1 | Acción 2 | ...",
  "minutes": "Minuta generada...",
  "executive_summary": "Resumen de máximo 30 palabras"
}
```

## 5. Probar errores

### Formato no soportado (.avi)

```bash
curl -X POST "http://localhost:8000/api/v1/process/file" \
  -F "file=@archivo.avi"
# Esperado: 415, mensaje con formatos permitidos
```

### Archivo > 500 MB

```bash
# Crear archivo grande (ejemplo)
dd if=/dev/zero of=grande.mp3 bs=1M count=600
curl -X POST "http://localhost:8000/api/v1/process/file" -F "file=@grande.mp3"
# Esperado: 400, mensaje de límite
```

## 6. Formatos soportados

| Categoría | Extensiones |
|-----------|-------------|
| Audio | MP3, WAV, M4A |
| Video | MP4, MOV, WEBM, MKV |
| Texto | TXT, MD (existente) |

## 7. Timeout UI (008) vs API (009)

La API tiene timeout de 15 min (PROCESSING_TIMEOUT_SEC=900). La UI (008-web-file-upload) usa 10 min por defecto. Si 009 está activo, considera alinear el timeout de la UI a 15 min para aprovechar el margen de la API (variable o configuración en la UI). Si la UI mantiene 10 min, el usuario verá "tardó demasiado" a los 10 min aunque la API seguiría procesando.

## 8. Referencias

- [Contract: Validación multimedia](./contracts/multimedia-validation.md)
- [Contract: Servicio de transcripción](./contracts/transcription-service.md)
- [Contract: API process multimedia](./contracts/api-process-multimedia.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
