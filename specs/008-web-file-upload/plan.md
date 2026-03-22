# Implementation Plan: Subir archivos desde la interfaz web

**Branch**: `008-web-file-upload` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/008-web-file-upload/spec.md`

## Summary

Extender la interfaz Gradio existente para ofrecer una experiencia completa de subida de archivos: aceptar multimedia (MP4, MOV, MP3, WAV, M4A) y texto (TXT, MD) hasta 500 MB, validar tipos y tamaño antes de enviar, mostrar feedback visual durante carga y procesamiento (timeout 10 min), visualizar resultados en secciones claras, mensajes de error amigables en español, y configuración de URL del servicio. El botón Procesar permanece deshabilitado sin archivo; tras procesar se desactiva hasta Limpiar (alineado con 007). La UI consume la API existente `POST /api/v1/process/file` y `POST /api/v1/process/text`.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Gradio, httpx, FastAPI (API consumida)  
**Storage**: N/A (archivos procesados en memoria; la UI no persiste)  
**Testing**: pytest (tests unitarios para validación de archivos; tests de integración UI)  
**Target Platform**: Linux/macOS (desarrollo local); navegador web  
**Project Type**: Web application (UI Gradio que consume API)  
**Performance Goals**: Feedback visible durante carga; timeout 10 min para procesamiento  
**Constraints**: Formatos MP4, MOV, MP3, WAV, M4A, TXT, MD; máx 500 MB; español; Procesar deshabilitado sin archivo  
**Scale/Scope**: Extensión de src/ui/app.py; posible módulo de validación (utils); componentes Gradio

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. Arquitectura de tres capas | ✅ | UI en Capa de Presentación; solo invoca API, sin lógica de negocio |
| II. Nodos autocontenidos | N/A | No modifica nodos del grafo |
| III. Formatos de salida | ✅ | La UI muestra lo que la API devuelve; sin cambios en esquema |
| IV. Robustez ante información incompleta | ✅ | Validación cliente (formatos, tamaño); mensajes amigables en errores |
| V. Modularidad y testabilidad | ✅ | Validación en módulo separable; UI testeable |
| VI. Agent Skills | ✅ | gradio, fastapi (API consumida)

**Gates**: PASS. No violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/008-web-file-upload/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (file validation, API response)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
meetmind/
├── src/
│   ├── ui/
│   │   ├── app.py                    # MODIFICAR: file_types multimedia, validación tamaño, timeout 10min
│   │   └── (opcional) utils.py       # CREAR: validate_file_format, validate_file_size, format_error_message
│   └── config.py                     # Ya tiene get_api_base_url(); FR-008 cumplido
│
├── tests/
│   ├── unit/
│   │   └── ui/
│   │       └── test_validation.py    # CREAR: tests validación formatos y tamaño
│   └── integration/
│       └── ui/                       # (opcional) tests E2E UI
│
└── (resto sin cambios)
```

**Structure Decision**: Extensión de la UI Gradio existente. La validación de formatos y tamaño puede residir en `app.py` o en `src/ui/utils.py` si se prioriza modularidad. La API actual (`/process/file`) soporta solo TXT/MD; cuando US-010 extienda la API a multimedia, la UI ya estará preparada. Si la API rechaza un formato aún no soportado, la UI mostrará mensaje amigable (FR-006).

## Complexity Tracking

> No violaciones de Constitución. Esta sección queda vacía.
