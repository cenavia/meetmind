# Data Model: Ver extracción de participantes

**Feature**: 003-participants-extraction | **Date**: 2025-03-21

## Entidades

### Participante (extracción)

| Atributo | Tipo   | Restricciones                          | Descripción                                      |
|----------|--------|----------------------------------------|--------------------------------------------------|
| nombre   | str    | Sin títulos (Dr., Ing., Sr., etc.)     | Nombre y apellido; variante más completa si hay múltiples menciones |
| orden    | implícito | Por primera aparición en raw_text   | Posición en la lista final                       |

**Reglas de validación**:
- Excluir términos genéricos: "persona", "alguien", "un participante".
- Excluir títulos/honoríficos: solo nombre y apellido.
- Deduplicar: cada persona aparece una sola vez.
- Preferir variante más completa cuando existan múltiples menciones (ej. "Juan Pérez" sobre "Juan").

### Lista de participantes (salida)

| Atributo   | Tipo | Restricciones                                    | Descripción                |
|------------|------|--------------------------------------------------|----------------------------|
| participants | str | Nombres separados por coma; orden primera aparición | Campo en MeetingState y ProcessMeetingResponse |
| valor vacío | str | Literal "No identificados" (nunca "")            | Cuando no hay participantes identificables |

### MeetingState (estado del grafo)

El campo `participants` ya existe en MeetingState. Esta feature lo popula mediante el nodo `extract_participants`:

```python
# MeetingState (existente; participants ahora poblado por extract_participants)
raw_text: str
participants: str           # Extraído por extract_participants; "No identificados" si vacío
topics: str
actions: str
minutes: str
executive_summary: str
```

### Modelo interno (extract_participants)

```python
# Pydantic para structured output del LLM
class ParticipantsExtraction(BaseModel):
    participants: list[str]  # Nombres extraídos; el nodo post-procesa (orden, dedup, formato)
```

## Flujo de datos

```
raw_text (de preprocess)
        ↓
extract_participants node
        ↓
LLM + structured output → list[str]
        ↓
Post-proceso: orden por primera aparición, dedup (ya en prompt), excluir títulos
        ↓
participants: str (nombres separados por coma) o "No identificados"
        ↓
merge en MeetingState
        ↓
mock_result (no sobrescribe participants)
        ↓
ProcessMeetingResponse.participants
```

## Validaciones por capa

| Capa  | Validación                                                                 |
|-------|----------------------------------------------------------------------------|
| Nodo  | Lista vacía → "No identificados"; excluir genéricos y títulos en prompt    |
| Nodo  | Orden por primera aparición aplicado en post-proceso                       |
| API   | Sin cambios; participants ya validado por el nodo                          |
