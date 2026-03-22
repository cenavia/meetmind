# Data Model: Ver acciones acordadas con responsables

**Feature**: 005-extract-actions | **Date**: 2026-03-21

## Entidades

### Par acción-responsable (extracción)

| Atributo   | Tipo | Restricciones                                       | Descripción                                       |
|------------|------|-----------------------------------------------------|---------------------------------------------------|
| action     | str  | Breve; sin "|" ni ";"                                  | Descripción de la acción acordada                 |
| responsible| str  | Nombre propio o "Por asignar"; sin "|" ni ";"         | Responsable identificado o "Por asignar"          |
| orden      | implícito | Por primera aparición de la acción en raw_text   | Posición en la lista final                        |

**Reglas de validación**:
- Responsable solo por nombre propio explícito; cargo sin nombre → "Por asignar".
- Varios responsables explícitos → usar el primero mencionado.
- Acciones redundantes → consolidar, preferir variante más específica.
- Reformular acción y responsable para no contener "|" ni ";".

### Lista de acciones (salida)

| Atributo   | Tipo | Restricciones                                                | Descripción                |
|------------|------|--------------------------------------------------------------|----------------------------|
| actions    | str  | Pares "acción \| responsable" separados por punto y coma     | Campo en MeetingState y ProcessMeetingResponse |
| valor vacío| str  | Literal "No hay acciones identificadas" (nunca "")            | Cuando no hay acciones identificables |

### MeetingState (estado del grafo)

El campo `actions` ya existe en MeetingState. Esta feature lo popula mediante el nodo `extract_actions`:

```python
# MeetingState (existente; actions ahora poblado por extract_actions)
raw_text: str
participants: str
topics: str
actions: str           # Extraído por extract_actions; "No hay acciones identificadas" si vacío
minutes: str
executive_summary: str
```

### Modelo interno (extract_actions)

```python
# Pydantic para structured output del LLM
class ActionItem(BaseModel):
    action: str
    responsible: str

class ActionsExtraction(BaseModel):
    actions: list[ActionItem]  # El nodo post-procesa (orden, formato, sanitizar)
```

## Flujo de datos

```
raw_text (de identify_topics o preprocess)
        ↓
extract_actions node
        ↓
LLM + structured output → list[ActionItem]
        ↓
Post-proceso: orden por primera aparición, sanitizar "|" y ";", formatear con " | " y "; "
        ↓
actions: str ("acción | responsable; acción2 | responsable2") o "No hay acciones identificadas"
        ↓
merge en MeetingState
        ↓
mock_result (no sobrescribe actions)
        ↓
ProcessMeetingResponse.actions
```

## Validaciones por capa

| Capa  | Validación                                                                 |
|-------|----------------------------------------------------------------------------|
| Nodo  | Lista vacía → "No hay acciones identificadas"                              |
| Nodo  | Orden por primera aparición aplicado en post-proceso                       |
| Nodo  | Sanitizar "|" y ";" en acción y responsable (reemplazar o reformular)     |
| Nodo  | Formato "acción | responsable" con "; " entre pares                          |
| API   | Sin cambios; actions ya validado por el nodo                                |
