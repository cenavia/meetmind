# Contract: Campo executive_summary (respuesta de procesamiento)

**Feature**: 007-executive-summary | **Aplica a**: `POST /api/v1/process/text`, `POST /api/v1/process/file`

---

## Formato

| Campo | Tipo | Descripción |
|-------|------|-------------|
| executive_summary | string | Resumen ejecutivo en español; máximo 30 palabras; síntesis de decisiones, acciones críticas y conclusiones; o mensaje fijo si sin datos |

## Reglas (007)

- **Cuando hay datos (participantes, temas y/o acciones)**: Resumen en español, máximo 30 palabras (conteo: split por espacios). Enfocado en decisiones tomadas, acciones críticas, conclusiones principales. Síntesis clara y accionable.
- **Cuando no hay participantes, temas ni acciones extraídos**: Literal `"Resumen: No se identificó información procesable en la reunión."` (nunca cadena vacía).
- **Idioma**: Siempre español.
- **Si el LLM excede 30 palabras**: Retry con prompt ajustado; fallback truncar en palabra 30.

## Ejemplos

| Escenario | executive_summary |
|-----------|-------------------|
| Con decisiones y acciones | `"Acuerdo sobre presupuesto. María envía informe; Juan prepara presentación."` (≤30 palabras) |
| Solo temas informativos | `"Reunión informativa. Temas: presupuesto, plazos, recursos."` (≤30 palabras) |
| Sin datos | `"Resumen: No se identificó información procesable en la reunión."` |
