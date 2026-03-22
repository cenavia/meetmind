# Contract: API REST MeetMind (US-010 / spec 012)

**Base URL**: configurable (ej. `http://localhost:8000`)  
**Prefijo API**: `/api/v1` para procesamiento y reuniones  
**Documentación interactiva**: `/docs` (Swagger UI), `/redoc` opcional (FastAPI)

## Autenticación

Ninguna en este entregable (entorno de confianza).

---

## Liveness

### `GET /health`

| Código | Cuerpo | Descripción |
|--------|--------|-------------|
| 200 | `{"status": "ok"}` | Proceso vivo |

No comprueba base de datos.

---

## Readiness

### `GET /ready`

| Código | Cuerpo | Descripción |
|--------|--------|-------------|
| 200 | `{"status": "ready"}` (ejemplo) | BD accesible para operaciones que la requieren |
| 503 | `{"detail": "..."}` | No preparado (p. ej. BD no accesible) |

*Nota de implementación: ruta exacta puede ajustarse siempre que la documentación OpenAPI y este contrato coincidan.*

---

## Procesamiento

### `POST /api/v1/process/text`

**Content-Type**: `application/json`

**Body**: `{ "text": "..." }`

| Código | Descripción |
|--------|-------------|
| 200 | `ProcessMeetingResponse` + `meeting_id` si aplica |
| 400 | Texto demasiado largo u otra regla documentada |
| 422 | Validación (texto vacío, JSON inválido) |
| 503/500 | Error servidor (p. ej. fallo persistencia tras éxito de grafo, según research) |

### `POST /api/v1/process/file`

**Content-Type**: `multipart/form-data` (campo archivo según implementación actual)

| Código | Descripción |
|--------|-------------|
| 200 | Resultado estructurado + `meeting_id` si aplica |
| 400 / 422 | Archivo no permitido, tamaño, formato |
| 503/500 | Error interno o persistencia |

*Streaming u otros subpath existentes: documentar en OpenAPI si permanecen públicos.*

---

## Reuniones persistidas

### `GET /api/v1/meetings`

| Código | Cuerpo |
|--------|--------|
| 200 | `{ "items": [ MeetingRecordResponse, ... ] }` — puede ser `[]` **solo** si BD respondió OK y no hay filas |
| 503 | Error servidor — **no** usar 200 con lista vacía para encubrir fallo de BD (FR-014) |

### `GET /api/v1/meetings/{meeting_id}`

| Código | Descripción |
|--------|-------------|
| 200 | Registro completo |
| 404 | Id válido pero no existe registro |
| 422 | UUID mal formado |
| 503 | Fallo de almacenamiento al leer (FR-014) — **no** 404 |

---

## Esquemas JSON (referencia)

Ver ejemplos en [../011-persist-meeting-records/contracts/meetings-api.md](../011-persist-meeting-records/contracts/meetings-api.md) para `MeetingRecordResponse`.

`ProcessMeetingResponse` incluye al menos los cinco campos de resultado; campo opcional `meeting_id` según [research.md](../research.md).
