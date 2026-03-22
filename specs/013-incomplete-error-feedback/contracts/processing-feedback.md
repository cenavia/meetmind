# Contract: Respuesta de procesamiento y feedback (spec 013)

**Alcance**: Complementa [spec 012 `openapi-rest.md`](../012-meetings-rest-api/contracts/openapi-rest.md) para el **cuerpo JSON de éxito** y **simetría** con GET `/api/v1/meetings/{id}`.

## Principios

- Mensajes orientados a persona en **español** (FR-015).
- **Sin** trazas de pila ni `traceback` en JSON público (FR-003, FR-013).
- `processing_errors` es siempre un **array de strings** (puede ser vacío).

## `ProcessMeetingResponse` (POST `/api/v1/process/text` y POST síncrono archivo cuando aplique)

```json
{
  "participants": "string",
  "topics": "string",
  "actions": "string",
  "minutes": "string",
  "executive_summary": "string",
  "meeting_id": "uuid-or-null",
  "status": "completed|partial|failed",
  "processing_errors": ["..."],
  "transcript": ""
}
```

| Campo | Reglas |
|-------|--------|
| status | Obligatorio en éxito HTTP 200 del procesamiento completado (incluso si `failed`/`partial`). |
| processing_errors | Lista completa; la UI muestra todos los ítems (scroll). |
| transcript | Texto transcrito si el flujo lo generó; si no aplica, cadena vacía u omisión según Pydantic (documentar en OpenAPI). |

## `MeetingRecordResponse` (GET listado y detalle)

Mismos campos `status`, `processing_errors` (array), y `transcript` si se persiste en una versión futura del modelo; si `transcript` no está en BD, omitir o `null` hasta que exista columna.

## SSE / stream multimedia

El evento terminal de éxito (`type: result` o equivalente actual) DEBE incluir los mismos campos lógicos que el JSON síncrono (`status`, `processing_errors` como lista, `transcript` si existe) para que Gradio no bifurque reglas.

## Errores (`4xx` / `5xx`)

- Cuerpo típico FastAPI: `{"detail": "..."}` o lista de validación; textos en español.
- No incluir `exception_type`, `stack`, ni variables de entorno.
