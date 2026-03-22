# Contract: Campo topics (respuesta de procesamiento)

**Feature**: 004-identify-topics | **Aplica a**: `POST /api/v1/process/text`, `POST /api/v1/process/file`

---

## Formato

| Campo   | Tipo   | Descripción                                                                 |
|---------|--------|-----------------------------------------------------------------------------|
| topics  | string | Temas principales separados por punto y coma, o literal "No hay temas identificados" |

## Reglas (004)

- **Cuando hay temas**: Entre 1 y 5 temas separados por punto y coma. Ejemplo: `"Presupuesto Q2; Plazos del proyecto; Asignación de recursos"`.
- **Cuando no hay temas identificables**: Literal `"No hay temas identificados"` (nunca cadena vacía).
- **Orden**: Por primera aparición en el texto de entrada.
- **Consolidación**: Temas solapados (ej. "Presupuesto" y "Presupuesto Q2") se consolidan en uno, preferiendo la variante más específica.
- **Granularidad**: Evitar temas genéricos ("Reunión de trabajo", "Discusión general"); priorizar temas concretos del contenido.

## Ejemplos

| Texto de entrada                                      | topics                                                     |
|-------------------------------------------------------|------------------------------------------------------------|
| "Se discutió presupuesto, plazos y recursos..."       | `"Presupuesto; Plazos; Recursos"` o similar                |
| "Reunión de coordinación..." (muy genérico)           | `"No hay temas identificados"` o 1 tema muy concreto       |
| "Sprint 12 y bugs del módulo de facturación..."       | `"Sprint 12; Módulo de facturación"` (no "Reunión de trabajo") |
| "Presupuesto Q2... el presupuesto trimestral..."      | `"Presupuesto Q2"` (consolidado, variante específica)      |
