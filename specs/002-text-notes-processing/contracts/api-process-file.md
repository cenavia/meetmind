# API Contract: Procesamiento de archivo (TXT/Markdown)

**Feature**: 002-text-notes-processing | **Base URL**: `{API_BASE_URL}` (default `http://localhost:8000`)

---

## POST /api/v1/process/file

Procesa un archivo de texto (.txt o .md) con notas de reunión y devuelve resultados estructurados. No ejecuta transcripción; el contenido se lee directamente y se pasa al workflow de extracción.

### Request

**Headers**:
- `Content-Type: multipart/form-data`

**Body** (form-data):
| Campo | Tipo | Requerido | Restricciones |
|-------|------|-----------|---------------|
| file | file | Sí | Extensión .txt o .md; MIME text/plain o text/markdown; contenido 1–50.000 caracteres tras lectura |

### Response 200

Mismo esquema que `POST /api/v1/process/text`:

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

**Formato no soportado** (ej. PDF, DOCX):
```json
{
  "detail": "Solo se admiten archivos .txt y .md"
}
```

**Contenido excede límite** (tras leer, >50.000 caracteres):
```json
{
  "detail": "El contenido excede el límite de 50000 caracteres"
}
```

### Response 422

**Archivo vacío o solo espacios**:
```json
{
  "detail": "El archivo está vacío o contiene solo espacios"
}
```

**Error de encoding** (no se pudo leer con UTF-8 ni latin-1):
```json
{
  "detail": "No se pudo interpretar el encoding del archivo. Use UTF-8 o Latin-1."
}
```

### Response 415

**MIME type no permitido**:
```json
{
  "detail": "Tipo de archivo no soportado. Solo text/plain y text/markdown."
}
```

### Códigos

| Código | Descripción |
|--------|-------------|
| 200 | Procesamiento correcto |
| 400 | Formato no soportado o contenido excede 50.000 caracteres |
| 415 | MIME type no permitido |
| 422 | Archivo vacío o error de encoding |
| 500 | Error interno del servidor |

### Ejemplo cURL

```bash
curl -X POST http://localhost:8000/api/v1/process/file \
  -F "file=@notas_reunion.txt"
```
