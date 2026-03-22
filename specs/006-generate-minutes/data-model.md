# Data Model: Ver minuta formal

**Feature**: 006-generate-minutes | **Date**: 2026-03-21

## Entidades

### Minuta (salida)

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| minutes | str | Máx. 150 palabras (conteo: split por espacios) | Texto narrativo continuo en español que resume la reunión |
| formato | implícito | Narrativo continuo, sin secciones con encabezados | Integra participantes, temas y acciones de forma fluida |
| idioma | implícito | Siempre español | |
| valor vacío | str | Literal "Minuta: No se identificó información procesable en la reunión." (nunca "") | Cuando no hay participantes, temas ni acciones extraídos |

**Reglas de validación**:
- Conteo de palabras: split por espacios en blanco; secuencias entre espacios cuentan como una palabra.
- Si el LLM devuelve >150 palabras: truncar preservando coherencia (límite de oración o palabra 150).
- Tono profesional y formal; legible y coherente con el contenido original.

### MeetingState (estado del grafo)

El campo `minutes` ya existe en MeetingState. Esta feature lo popula mediante el nodo `generate_minutes`:

```python
# MeetingState (existente; minutes ahora poblado por generate_minutes)
raw_text: str
participants: str
topics: str
actions: str
minutes: str           # Generado por generate_minutes; mensaje fijo si sin datos
executive_summary: str
```

## Flujo de datos

```
participants, topics, actions (de extract_participants, identify_topics, extract_actions)
        ↓
generate_minutes node
        ↓
¿Todos vacíos / "sin datos"? → Sí → minutes: "Minuta: No se identificó información procesable en la reunión."
        ↓ No
LLM (prompt con participants, topics, actions) → texto narrativo
        ↓
Post-proceso: contar palabras (split por espacios); si >150 → truncar
        ↓
minutes: str (≤150 palabras)
        ↓
merge en MeetingState
        ↓
mock_result (no sobrescribe minutes)
        ↓
ProcessMeetingResponse.minutes
```

## Validaciones por capa

| Capa | Validación |
|------|------------|
| Nodo | Sin datos → "Minuta: No se identificó información procesable en la reunión." |
| Nodo | Conteo palabras: split por espacios; si >150 → truncar |
| Nodo | Tono profesional, español, narrativo continuo (instrucciones en prompt) |
| API | Sin cambios; minutes ya validado por el nodo |
