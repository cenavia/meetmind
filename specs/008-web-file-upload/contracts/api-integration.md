# Contract: Integración UI con API

**Feature**: 008-web-file-upload | **Aplica a**: `process_meeting_file`, `process_meeting_text`

---

## Endpoints consumidos

| Método | Ruta | Uso |
|--------|------|-----|
| POST | `/api/v1/process/file` | Procesar archivo (multipart) |
| POST | `/api/v1/process/text` | Procesar texto plano |

**URL base**: `API_BASE_URL` (variable de entorno), default `http://localhost:8000`.

---

## Timeout

- **Archivo**: 600 segundos (10 minutos)
- **Texto**: 600 segundos (alineado; procesamiento puede ser largo)

---

## Respuesta esperada (200 OK)

```json
{
  "participants": "string",
  "topics": "string",
  "actions": "string",
  "minutes": "string",
  "executive_summary": "string"
}
```

---

## Errores y presentación al usuario

| Código / Excepción | Presentación |
|--------------------|--------------|
| httpx.ConnectError | "No se puede conectar con la API. Verifica que esté ejecutándose en la URL configurada." |
| httpx.TimeoutException | "El procesamiento tardó demasiado. Intenta de nuevo o usa un archivo más corto." |
| HTTP 4xx/5xx | Extraer `detail` del JSON si existe; presentar mensaje amigable; no exponer código HTTP ni stack trace |

---

## Formato de presentación de resultados

La UI formatea la respuesta como Markdown:

```markdown
## Participantes
{participants}

## Temas
{topics}

## Acciones
{actions}

## Minuta
{minutes}

## Resumen ejecutivo
{executive_summary}
```
