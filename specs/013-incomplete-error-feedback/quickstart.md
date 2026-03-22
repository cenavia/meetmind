# Quickstart: verificar feedback y errores (013)

**Date**: 2026-03-22

## Prerrequisitos

- Entorno con dependencias instaladas (`uv sync` o equivalente).
- Variables en `.env` según `.env.example` (API URL para UI, transcripción, BD).

## 1. API

```bash
cd /Users/consultor/Documents/projects/meetmind
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

- `POST /api/v1/process/text` con texto de **menos de 20 palabras** → respuesta 200 con `status` `partial` (o según reglas), `processing_errors` **no vacía**, mensajes en español.
- Misma ruta con texto vacío → **422** con `detail` comprensible.
- Revisar en Swagger `/docs` que el esquema muestra `processing_errors` como **array**.

## 2. UI

```bash
uv run gradio src/ui/app.py
```

- Procesar sin texto ni archivo → mensaje junto al flujo de acción, en español.
- Tras procesamiento con advertencias → bloque **Avisos** separado del Markdown de análisis; lista completa con scroll si hay muchas entradas.
- Estado **Completado / Parcial / Error** visible como **texto**, no solo color.
- Con archivo multimedia y transcripción OK → sección **Transcripción** con acción **Copiar**.
- Expandir **Detalles técnicos** → sin secretos; colapsado al cargar.

## 3. Tests automáticos

```bash
cd /Users/consultor/Documents/projects/meetmind/src
pytest ../tests/unit ../tests/integration/api -q
```

Añadir/ajustar casos que validen forma de `processing_errors` y ausencia de subcadenas tipo `Traceback` en respuestas de error simuladas.

## 4. Historial (cuando exista en UI)

Abrir un registro `partial` o `failed` desde historial y confirmar el mismo patrón visual que en procesamiento principal (FR-012).
