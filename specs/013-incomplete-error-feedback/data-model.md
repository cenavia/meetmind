# Data Model: Feedback y errores (013)

**Feature**: 013-incomplete-error-feedback | **Date**: 2026-03-22

## Estado del grafo (`MeetingState`)

| Campo | Tipo lógico | Notas |
|-------|---------------|--------|
| raw_text | str | Entrada normalizada (strip) |
| participants | str | Formato PRD |
| topics | str | Formato PRD |
| actions | str | Formato PRD |
| minutes | str | Formato PRD |
| executive_summary | str | Formato PRD |
| processing_errors | **list[str]** | Advertencias y errores no fatales acumulados; mensajes en español |
| transcript | str (opcional) | Texto transcrito si el flujo incluyó STT; vacío si no aplica |

**Transiciones**: Los nodos devuelven parciales `{"processing_errors": ["..."]}` que el reducer concatena. No se borra la lista salvo decisión explícita de diseño en un nodo concreto (evitar).

## Respuesta API: procesamiento síncrono (`ProcessMeetingResponse`)

Extensión respecto al modelo actual:

| Campo | Tipo | Obligatorio | Notas |
|-------|------|-------------|--------|
| participants | str | sí | |
| topics | str | sí | |
| actions | str | sí | |
| minutes | str | sí | |
| executive_summary | str | sí | |
| meeting_id | UUID \| null | no | Si persistencia OK |
| **status** | str | sí | `completed` \| `partial` \| `failed` |
| **processing_errors** | list[str] | sí | Puede ser `[]` |
| **transcript** | str | no | Omisión o `""` si no hubo transcripción |

**Validación**: `status` acotado a los tres valores; strings de salida PRD sin cambio de formato.

## Respuesta API: reunión persistida (`MeetingRecordResponse`)

Alinear con lo anterior:

| Campo | Tipo | Notas |
|-------|------|--------|
| … campos existentes … | | |
| status | str | `completed` \| `partial` \| `failed` |
| processing_errors | **list[str]** | Deserializado desde BD |

## Persistencia (`MeetingRecord`)

| Campo DB | Tipo físico | Representación |
|----------|-------------|----------------|
| processing_errors | Text | **JSON array de strings** (`["msg1","msg2"]`). Filas legacy: parser tolerante (si no es JSON válido, tratar como `[valor_crudo]` o `[]` según regla en `repository`/`meeting_persist`). |

**Migración**: Opcional script o migración Alembic si se exige backfill; para MVP, lectura tolerante + escritura solo en formato nuevo.

## Reglas de `status` (negocio)

- **failed**: Fallo de transcripción obligatoria, fallo irrecuperable del pipeline, o registro creado solo vía `persist_failed`.
- **partial**: Hay `processing_errors` no vacía **o** señales de calidad limitada acordadas (p. ej. prefijo `[Información limitada]` en minuta/resumen según lógica actual en `status_from_graph_result`) **sin** fallo global.
- **completed**: Sin errores acumulados y salidas consideradas completas según reglas existentes.

*(La implementación debe unificar `status_from_graph_result` con el DTO de POST para evitar divergencias.)*

## Errores HTTP (cuerpo)

- `detail` en español, string o lista de errores de validación FastAPI **sin** stack traces.
- Códigos existentes: 400/408/415/422/503/500 según contexto; documentados en contrato.
