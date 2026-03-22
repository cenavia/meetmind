# Contract: Campo minutes (respuesta de procesamiento)

**Feature**: 006-generate-minutes | **Aplica a**: `POST /api/v1/process/text`, `POST /api/v1/process/file`

---

## Formato

| Campo   | Tipo   | Descripción                                                                 |
|---------|--------|-----------------------------------------------------------------------------|
| minutes | string | Minuta formal en español; texto narrativo continuo; máximo 150 palabras; o mensaje fijo si sin datos |

## Reglas (006)

- **Cuando hay datos (participantes, temas y/o acciones)**: Minuta en español, tono profesional, texto narrativo continuo (párrafos fluidos) integrando la información disponible. Máximo 150 palabras (conteo: split por espacios).
- **Cuando no hay participantes, temas ni acciones extraídos**: Literal `"Minuta: No se identificó información procesable en la reunión."` (nunca cadena vacía).
- **Idioma**: Siempre español.
- **Estructura**: Sin secciones con encabezados explícitos; narrativa fluida.
- **Información parcial**: Integrar solo lo disponible; no inventar secciones ni datos inexistentes.

## Ejemplos

| Escenario | minutes |
|-----------|---------|
| Con participantes, temas y acciones | `"Reunión con Juan y María. Se discutieron el presupuesto trimestral y los plazos del proyecto. María enviará el informe antes del viernes; Juan preparará la presentación."` (≤150 palabras) |
| Solo temas | `"Reunión de seguimiento. Temas tratados: presupuesto, plazos y recursos. No se identificaron acciones concretas."` (≤150 palabras) |
| Sin datos | `"Minuta: No se identificó información procesable en la reunión."` |
