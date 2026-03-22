# Data Model: 012-meetings-rest-api

**Feature**: 012-meetings-rest-api | **Date**: 2026-03-22

## Persistencia

Sin nuevas tablas. Reutilizar **`MeetingRecord`** (011): ver [../011-persist-meeting-records/data-model.md](../011-persist-meeting-records/data-model.md).

## DTOs HTTP (API)

### `ProcessTextRequest`

| Campo | Tipo | Reglas |
|-------|------|--------|
| text | string | 1…50 000 caracteres (validación Pydantic); vacío/solo espacios → 422 tras normalización en handler |

### `ProcessMeetingResponse` (ampliación recomendada)

| Campo | Tipo | Notas |
|-------|------|--------|
| participants | string | PRD |
| topics | string | PRD |
| actions | string | PRD |
| minutes | string | PRD |
| executive_summary | string | PRD |
| meeting_id | UUID \| null | Opcional; presente si persistencia creó registro |

### `MeetingRecordResponse` / `MeetingRecordListResponse`

Sin cambio semántico respecto a 011: listado en `items`, orden `created_at` DESC.

### Health

| Operación | Cuerpo típico | Códigos |
|-----------|---------------|---------|
| Liveness | `{"status": "ok"}` | 200 |
| Readiness OK | `{"status": "ready"}` o equivalente documentado | 200 |
| Readiness fail | `detail` claro | 503 (recomendado) |

## Reglas de validación (negocio API)

- Archivo multipart: MIME/extensiones y tamaño según `multimedia_validation` y config.
- **FR-014**: error de lectura BD en list/get → respuesta de error servidor, no éxito con cuerpo “vacío” engañoso.

## Relaciones

Ninguna nueva; lectura/escritura vía `MeetingRepository`.
