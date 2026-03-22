# Data Model: Hello World E2E

**Feature**: 001-hello-world-e2e | **Date**: 2025-03-21

## Alcance

En esta fase no hay persistencia. El modelo describe únicamente el estado interno del grafo LangGraph y los DTOs de la API (request/response).

---

## 1. MeetingState (LangGraph)

Estado compartido del grafo. Definido en `src/agents/meeting/state.py`.

| Campo | Tipo | Origen | Descripción |
|-------|------|--------|-------------|
| `raw_text` | `str` | Input | Texto de entrada de la reunión |
| `participants` | `str` | mock_result | Nombres separados por coma |
| `topics` | `str` | mock_result | 3-5 temas; separador punto y coma |
| `actions` | `str` | mock_result | Acciones separadas por pipe (\|) |
| `minutes` | `str` | mock_result | Minuta formal (máx. 150 palabras) |
| `executive_summary` | `str` | mock_result | Resumen ejecutivo (máx. 30 palabras) |

**Validación**: En Hello World (mock) no se validan restricciones de longitud; los valores hardcodeados cumplen el formato. En fases posteriores, los nodos reales aplicarán las reglas de Constitución III.

---

## 2. Request: Procesar texto

**Endpoint**: `POST /api/v1/process/text`

| Campo | Tipo | Requerido | Validación | Descripción |
|-------|------|-----------|------------|-------------|
| `text` | `str` | Sí | 1 ≤ len ≤ 50.000; trim de espacios | Texto de la reunión |

**Ejemplo**:
```json
{
  "text": "Reunión con Juan y María. Discutimos el presupuesto y las fechas."
}
```

**Errores**:
- 422: `text` vacío o solo espacios
- 400: `text` > 50.000 caracteres

---

## 3. Response: Resultado de procesamiento

**Endpoint**: `POST /api/v1/process/text` (200)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `participants` | `str` | Nombres separados por coma |
| `topics` | `str` | Temas separados por punto y coma |
| `actions` | `str` | Acciones separadas por pipe |
| `minutes` | `str` | Minuta narrativa |
| `executive_summary` | `str` | Resumen ejecutivo |

**Ejemplo (mock)**:
```json
{
  "participants": "Juan, María",
  "topics": "Presupuesto; Fechas de entrega",
  "actions": "Revisar cifras|Juan | Enviar propuesta|María",
  "minutes": "Reunión de seguimiento. Se revisó el estado del presupuesto. Se acordó enviar propuesta actualizada antes del viernes.",
  "executive_summary": "Acuerdo sobre presupuesto y plazos."
}
```

---

## 4. Health Response

**Endpoint**: `GET /health`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `status` | `str` | "ok" o "healthy" |
| (opcional) | | Otros campos como `version` si se desea |

---

## 5. Entidades de dominio (solo conceptuales)

Para referencia futura; no se persisten en Hello World:

- **Participante**: persona identificada en la reunión
- **Tema**: asunto tratado
- **Acción**: compromiso con posible responsable
- **Minuta**: resumen narrativo formal
- **Resumen ejecutivo**: síntesis de alto nivel
