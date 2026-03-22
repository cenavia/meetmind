# Contract: API de reuniones persistidas

**Feature**: 011-persist-meeting-records | **Base path**: `/api/v1` (mismo prefijo que `process`)

## Autenticación

Ninguna en este entregable (entorno de confianza, FR-009).

---

## GET /meetings/{meeting_id}

**Descripción**: Recupera un registro completo por UUID.

**Path params**:

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| meeting_id | UUID (string) | Identificador del registro |

**Respuestas**:

| Código | Cuerpo | Descripción |
|--------|--------|-------------|
| 200 | `MeetingRecordResponse` | Registro encontrado |
| 404 | `{"detail": "..."}` | No existe reunión con ese id (mensaje claro en español) |
| 422 | FastAPI validation | `meeting_id` con formato inválido |

**MeetingRecordResponse** (JSON, `application/json`):

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "participants": "Ana, Luis",
  "topics": "Presupuesto; Planificación",
  "actions": "Revisar informe | Ana",
  "minutes": "...",
  "executive_summary": "...",
  "source_file_name": "reunion.md",
  "source_file_type": "text/markdown",
  "status": "completed",
  "created_at": "2026-03-22T12:00:00Z",
  "processing_errors": null
}
```

- `created_at`: ISO 8601 con zona (recomendado UTC con sufijo `Z`).
- `processing_errors`: string o `null`.

---

## GET /meetings

**Descripción**: Lista **todas** las reuniones almacenadas, ordenadas por `created_at` **descendente** (más reciente primero, FR-007).

**Query params**: ninguno en esta historia (sin paginación).

**Respuestas**:

| Código | Cuerpo | Descripción |
|--------|--------|-------------|
| 200 | `MeetingRecordListResponse` | Lista (posiblemente vacía) |

**MeetingRecordListResponse**:

```json
{
  "items": [ /* 0..N MeetingRecordResponse, ordenados por created_at DESC */ ]
}
```

---

## Comportamiento compartido

- Los campos de texto reflejan lo persistido en el momento del `create`; no hay PATCH/DELETE en este contrato.
- Errores 404/422 no filtran datos de otros registros.

## Integración con POST /process/*

La creación de registros **no** amplía el cuerpo de `ProcessMeetingResponse` en el MVP (evita romper la UI). Opcional futuro: añadir `meeting_id` en la respuesta de proceso para enlace directo al historial.
