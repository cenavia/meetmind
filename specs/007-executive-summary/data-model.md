# Data Model: Ver resumen ejecutivo

**Feature**: 007-executive-summary | **Date**: 2026-03-21

## Entidades

### Resumen ejecutivo (salida)

| Atributo | Tipo | Restricciones | Descripción |
|----------|------|---------------|-------------|
| executive_summary | str | Máx. 30 palabras (conteo: split por espacios) | Síntesis ultra-concisa: decisiones, acciones críticas, conclusiones principales |
| formato | implícito | Texto libre, ultra-conciso | Permite a Elena decidir si leer la minuta completa |
| idioma | implícito | Siempre español | |
| valor vacío | str | Literal "Resumen: No se identificó información procesable en la reunión." (nunca "") | Cuando no hay participantes, temas ni acciones extraídos |

**Reglas de validación**:
- Conteo de palabras: split por espacios en blanco; secuencias entre espacios cuentan como una palabra (alineado con 006).
- Si el LLM devuelve >30 palabras: retry con prompt ajustado (máx. 2 reintentos); fallback: truncar en palabra 30.
- Contenido: decisiones, acciones críticas, conclusiones principales; tono profesional.
- Para reuniones informativas: sintetizar temas principales.

### MeetingState (estado del grafo)

El campo `executive_summary` ya existe en MeetingState. Esta feature lo popula mediante el nodo `create_summary`:

```python
# MeetingState (existente; executive_summary ahora poblado por create_summary)
raw_text: str
participants: str
topics: str
actions: str
minutes: str
executive_summary: str  # Generado por create_summary; mensaje fijo si sin datos
```

### Estado de UI (Procesar/Limpiar)

| Estado | process_btn.interactive | Descripción |
|--------|-------------------------|-------------|
| Sin contenido (texto/archivo vacío) | False | No se puede procesar |
| Con contenido, pre-procesar | True | Usuario puede hacer clic en Procesar |
| Tras clic en Procesar (inmediato) | False | Se desactiva al instante |
| Post-procesamiento (completado o error) | False | Permanece desactivado |
| Tras clic en Limpiar | False | Campos vacíos; si usuario añade contenido de nuevo → True |

## Flujo de datos

```
participants, topics, actions, minutes (de nodos previos)
        ↓
create_summary node
        ↓
¿Todos vacíos / "sin datos"? → Sí → executive_summary: "Resumen: No se identificó información procesable en la reunión."
        ↓ No
LLM (prompt con participants, topics, actions, minutes) → resumen
        ↓
¿Palabras > 30? → Sí → Retry con prompt ajustado (máx. 2 reintentos)
        ↓ No (o fallback truncar)
executive_summary: str (≤30 palabras)
        ↓
merge en MeetingState
        ↓
mock_result (no sobrescribe executive_summary)
        ↓
ProcessMeetingResponse.executive_summary
```

## Validaciones por capa

| Capa | Validación |
|------|------------|
| Nodo | Sin datos → "Resumen: No se identificó información procesable en la reunión." |
| Nodo | Conteo palabras: split por espacios; si >30 → retry (máx. 2) o truncar |
| Nodo | Contenido: decisiones, acciones, conclusiones; español; tono profesional |
| API | Sin cambios; executive_summary ya validado por el nodo |
| UI | Procesar se desactiva al clic; Limpiar restablece flujo; cambio de texto/archivo reactiva Procesar si hay contenido |
