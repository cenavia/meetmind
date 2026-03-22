# Implementation Plan: Procesar grabación multimedia

**Branch**: `009-multimedia-recording` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/009-multimedia-recording/spec.md`

## Summary

Extender la API y el flujo de procesamiento para aceptar archivos multimedia (audio: MP3, WAV, M4A; video: MP4, MOV, WEBM, MKV), transcribirlos mediante un servicio STT (Whisper), extraer audio de video con ffmpeg, y ejecutar el workflow estándar sobre la transcripción. Límite 500 MB, timeout 15 min (síncrono); si se supera, flujo asíncrono con job ID para consulta posterior. Mensajes en español. La UI (008) ya soporta estos formatos; la API actual solo TXT/MD — esta feature añade la capa backend.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, LangGraph, LangChain, openai-whisper, ffmpeg (sistema), pydub (opcional para extracción de audio)  
**Storage**: SQLModel/DB para jobs asíncronos (cuando supera timeout); transcripciones en memoria para flujo síncrono  
**Testing**: pytest (unit: transcripción, validación; integration: endpoint multimedia)  
**Target Platform**: Linux/macOS (ffmpeg instalado); API servida por uvicorn  
**Project Type**: Web service (API FastAPI que consume LangGraph)  
**Performance Goals**: Transcripción síncrona hasta 15 min; feedback durante procesamiento  
**Constraints**: Formatos MP4, MOV, MP3, WAV, M4A, WEBM, MKV; máx 500 MB; timeout 15 min; mensajes en español; codecs no soportados → rechazo amigable  
**Scale/Scope**: Nuevo servicio `transcription.py`; modificación de `process.py` (API). Sin cambios en preprocess ni file_loader; transcripción en API. Flujo async (FR-007/FR-010) diferido a iteración futura.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | API en Capa API; transcripción y workflow en Capa Negocio; sin lógica en UI |
| II. Nodos autocontenidos | ✅ | Transcripción como servicio en src/services; preprocess sin cambios |
| III. Formatos de salida | ✅ | Sin cambios en esquema; mismo output que texto |
| IV. Robustez ante información incompleta | ✅ | Transcripción fallida → processing_errors; rechazo por codec/archivo corrupto |
| V. Modularidad y testabilidad | ✅ | Servicio de transcripción separable; tests unitarios por componente |
| VI. Agent Skills | ✅ | langgraph-fundamentals, fastapi, langchain-dependencies |

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/009-multimedia-recording/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (multimedia validation, transcription, async job)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── api/
│   │   └── routers/
│   │       └── process.py           # MODIFICAR: aceptar multimedia; validar MIME, tamaño; transcribir o cargar texto
│   ├── agents/
│   │   └── meeting/
│   │       └── nodes/
│   │           └── preprocess/
│   │               └── node.py      # SIN CAMBIOS: transcripción en API antes de invocar grafo
│   ├── services/
│   │   ├── file_loader.py           # SIN CAMBIOS: texto (.txt, .md) se delega a load_text_file existente
│   │   ├── transcription.py         # CREAR: transcribir audio con Whisper; extraer audio de video (ffmpeg)
│   │   └── (futuro) async_jobs.py   # DIFERIDO: FR-007/FR-010 (flujo async tras timeout) en iteración futura
│   ├── config.py                    # MODIFICAR: TRANSCRIPTION_MODEL, MAX_FILE_SIZE_MB, PROCESSING_TIMEOUT_SEC
│   └── db/                          # (si async) modelo Job para consulta posterior
│
├── tests/
│   ├── unit/
│   │   ├── services/
│   │   │   └── test_transcription.py  # CREAR: tests transcripción (mock Whisper)
│   │   └── api/
│   │       └── test_process_multimedia.py  # CREAR: tests validación multimedia
│   └── integration/
│       └── api/
│           └── test_process_file_multimedia.py  # CREAR: E2E con archivo MP3/MP4
│
└── pyproject.toml                   # MODIFICAR: openai-whisper, pydub (opcional)
```

**Structure Decision**: Extensión del backend existente. La transcripción se implementa como servicio en `src/services/transcription.py`. El flujo: API recibe archivo → si multimedia, transcribir → si texto, cargar (file_loader existente) → invocar grafo con raw_text. El nodo preprocess no se modifica; la transcripción ocurre en la API antes de invocar el grafo. **Diferido**: FR-007 (flujo asíncrono tras timeout) y FR-010 (job ID, GET /jobs/{id}) se implementan en una iteración futura; el MVP devuelve HTTP 408 en timeout.

## Complexity Tracking

| Diferido | Razón |
|----------|-------|
| FR-007 (flujo async tras timeout) | MVP prioriza flujo síncrono; timeout → HTTP 408. Async (job ID, consulta posterior) en iteración futura. |
| FR-010 (job ID, GET /jobs/{id}) | Requiere almacén de jobs; bloqueado por decisión de FR-007. |
