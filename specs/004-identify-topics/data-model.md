# Data Model: Ver temas principales discutidos

**Feature**: 004-identify-topics | **Date**: 2026-03-21

## Entidades

### Tema principal (extracción)

| Atributo | Tipo   | Restricciones                          | Descripción                                      |
|----------|--------|----------------------------------------|--------------------------------------------------|
| texto    | str    | Granularidad apropiada; no genérico    | Tema discutido; variante más específica si hay solapados |
| orden    | implícito | Por primera aparición en raw_text   | Posición en la lista final                       |

**Reglas de validación**:
- Evitar temas genéricos: "Reunión", "Discusión general", "Reunión de trabajo".
- Consolidar temas solapados: preferir variante más específica (ej. "Presupuesto Q2" en lugar de "Presupuesto" y "Presupuesto Q2").
- Entre 1 y 5 temas; si hay menos identificables, retornar los disponibles sin forzar relleno.
- Orden por primera aparición en el texto.

### Lista de temas (salida)

| Atributo   | Tipo | Restricciones                                    | Descripción                |
|------------|------|--------------------------------------------------|----------------------------|
| topics     | str  | Temas separados por punto y coma; orden primera aparición | Campo en MeetingState y ProcessMeetingResponse |
| valor vacío| str  | Literal "No hay temas identificados" (nunca "")   | Cuando no hay temas identificables |

### MeetingState (estado del grafo)

El campo `topics` ya existe en MeetingState. Esta feature lo popula mediante el nodo `identify_topics`:

```python
# MeetingState (existente; topics ahora poblado por identify_topics)
raw_text: str
participants: str
topics: str           # Extraído por identify_topics; "No hay temas identificados" si vacío
actions: str
minutes: str
executive_summary: str
```

### Modelo interno (identify_topics)

```python
# Pydantic para structured output del LLM
class TopicsExtraction(BaseModel):
    topics: list[str]  # 1-5 temas; el nodo post-procesa (orden, formato)
```

## Flujo de datos

```
raw_text (de preprocess / extract_participants)
        ↓
identify_topics node
        ↓
LLM + structured output → list[str]
        ↓
Post-proceso: orden por primera aparición, formatear con "; "
        ↓
topics: str (temas separados por punto y coma) o "No hay temas identificados"
        ↓
merge en MeetingState
        ↓
mock_result (no sobrescribe topics)
        ↓
ProcessMeetingResponse.topics
```

## Validaciones por capa

| Capa  | Validación                                                                 |
|-------|----------------------------------------------------------------------------|
| Nodo  | Lista vacía → "No hay temas identificados"; restricción 3-5 en prompt      |
| Nodo  | Orden por primera aparición aplicado en post-proceso                       |
| Nodo  | Consolidación de solapados instruida en prompt; LLM aplica                 |
| API   | Sin cambios; topics ya validado por el nodo                                |
