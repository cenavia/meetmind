# Data Model: Almacenamiento persistente de reuniones procesadas

**Feature**: 011-persist-meeting-records | **Date**: 2026-03-22

## Entidad: MeetingRecord (reunión procesada)

Representa **una ejecución completada** del pipeline (éxito, fallo o parcial), no deduplica por archivo (FR-011).

| Campo | Tipo lógico | Obligatorio | Reglas / notas |
|-------|-------------|-------------|----------------|
| id | UUID (string en API) | sí | Generado al crear; inmutable; clave primaria |
| participants | str | sí | Formato PRD: nombres separados por coma; puede ser vacío en `failed` |
| topics | str | sí | Punto y coma; puede ser vacío en `failed` |
| actions | str | sí | Pipe `\|`; puede ser vacío en `failed` |
| minutes | str | sí | Minuta; puede ser vacío en `failed` |
| executive_summary | str | sí | Resumen ejecutivo; puede ser vacío en `failed` |
| source_file_name | str \| null | no | Nombre original si hubo archivo de entrada |
| source_file_type | str \| null | no | MIME o tipo lógico si disponible (p. ej. `text/plain`, extensión) |
| status | enum | sí | `completed` \| `failed` \| `partial` (valores estables en API y BD) |
| created_at | datetime (UTC) | sí | Auto al insertar; ordenación listado DESC |
| processing_errors | str \| null | no | Texto humano; múltiples mensajes pueden concatenarse con separador claro (p. ej. newline) |

### Validación

- `status` debe ser uno de los tres valores permitidos (validación Pydantic / constraint CHECK en BD si aplica).
- Longitudes de texto: acotadas por las mismas reglas que el procesamiento actual (p. ej. texto entrada 50k); salidas ya limitadas por nodos/PRD.

### Relaciones

- Ninguna en esta historia (tabla única).

### Transiciones de estado

- El estado se **asigna al crear** el registro; no hay máquina de estados ni actualización de filas en el alcance actual (sin UPDATE).

### Índices recomendados

- Índice o clúster por `created_at DESC` para listados eficientes (según volumen).
- PK en `id`.

## Mapeo desde `ProcessMeetingResponse` y rutas

| Origen API / grafo | Campo persistido |
|--------------------|------------------|
| `participants` | `participants` |
| `topics` | `topics` |
| `actions` | `actions` |
| `minutes` | `minutes` |
| `executive_summary` | `executive_summary` |
| `UploadFile.filename` / nombre lógico | `source_file_name` |
| `UploadFile.content_type` o extensión | `source_file_type` |
| — | `status`, `processing_errors`, `created_at`, `id` |

Para **POST /text** sin archivo: `source_file_name` y `source_file_type` nulos.

## DTOs HTTP (lectura)

Los GET devuelven un objeto alineado a la tabla anterior (nombres JSON en `snake_case`, `id` como string UUID) para consistencia con el resto de la API.
