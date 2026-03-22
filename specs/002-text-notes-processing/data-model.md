# Data Model: Procesar notas en texto

**Feature**: 002-text-notes-processing | **Date**: 2025-03-21

## Entidades

### Archivo de notas (entrada)

| Atributo    | Tipo   | Restricciones                          | Descripción                          |
|------------|--------|----------------------------------------|--------------------------------------|
| formato    | enum   | `.txt`, `.md`                          | Extensión permitida                  |
| mime_type  | enum   | `text/plain`, `text/markdown`          | MIME validado                        |
| contenido  | str    | 1–50.000 caracteres, UTF-8 o latin-1   | Texto extraído tras lectura          |
| encoding   | str    | `utf-8`, `latin-1`                     | Encoding detectado/usado             |

**Reglas de validación**:
- Extensión y MIME deben coincidir con formatos soportados.
- Contenido no vacío tras strip; longitud ≤ 50.000 caracteres.
- Encoding: intentar UTF-8; si falla, latin-1; si ambos fallan, rechazar.

### Documentación estructurada (salida)

Sin cambios respecto a 001. Esquema existente:

| Campo             | Tipo | Restricción (PRD)                    |
|-------------------|------|--------------------------------------|
| participants      | str  | Nombres separados por coma           |
| topics            | str  | 3-5 elementos; punto y coma          |
| actions           | str  | Separadas por pipe (\|)              |
| minutes           | str  | Máx. 150 palabras                    |
| executive_summary | str  | Máx. 30 palabras                     |

### MeetingState (estado del grafo)

No se modifica el esquema. La API inyecta `raw_text` (ya extraído del archivo o del body JSON) antes de invocar el grafo:

```python
# MeetingState (existente)
raw_text: str           # Entrada normalizada (texto o contenido de archivo)
participants: str
topics: str
actions: str
minutes: str
executive_summary: str
```

## Flujo de datos

```
Usuario sube .txt/.md
        ↓
API recibe UploadFile
        ↓
file_loader.load() → str (contenido)
        ↓
Validaciones (vacío, longitud, formato)
        ↓
graph.invoke({"raw_text": contenido})
        ↓
ProcessMeetingResponse (5 campos)
```

## Validaciones por capa

| Capa   | Validación                                                |
|--------|-----------------------------------------------------------|
| API    | Extensión, MIME, archivo no vacío, longitud ≤ 50k         |
| Services| Encoding (UTF-8, fallback latin-1), lectura correcta      |
| Core   | Ninguna adicional; recibe raw_text ya validado            |
