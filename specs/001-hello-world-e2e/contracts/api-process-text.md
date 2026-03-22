# API Contract: Procesamiento de texto

**Feature**: 001-hello-world-e2e | **Base URL**: `{API_BASE_URL}` (default `http://localhost:8000`)

---

## GET /health

Health check del servicio.

### Request

```
GET /health
```

### Response 200

```json
{
  "status": "ok"
}
```

### Códigos

| Código | Descripción |
|--------|-------------|
| 200 | Servicio operativo |

---

## POST /api/v1/process/text

Procesa texto de reunión y devuelve resultados estructurados.

### Request

**Headers**:
- `Content-Type: application/json`

**Body**:
```json
{
  "text": "string"
}
```

| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| text | string | Sí | 1–50.000 caracteres (después de trim) |

### Response 200

```json
{
  "participants": "string",
  "topics": "string",
  "actions": "string",
  "minutes": "string",
  "executive_summary": "string"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| participants | string | Nombres separados por coma |
| topics | string | Temas separados por punto y coma |
| actions | string | Acciones separadas por pipe (\|) |
| minutes | string | Minuta narrativa |
| executive_summary | string | Resumen ejecutivo |

### Response 400

Texto excede el límite de longitud:

```json
{
  "detail": "El texto excede el límite de 50000 caracteres"
}
```

### Response 422

Validación fallida (texto vacío):

```json
{
  "detail": [
    {
      "loc": ["body", "text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Códigos

| Código | Descripción |
|--------|-------------|
| 200 | Procesamiento correcto |
| 400 | Texto demasiado largo |
| 422 | Texto vacío o inválido |
| 500 | Error interno del servidor |
