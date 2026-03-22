# Contract: Campo actions (respuesta de procesamiento)

**Feature**: 005-extract-actions | **Aplica a**: `POST /api/v1/process/text`, `POST /api/v1/process/file`

---

## Formato

| Campo   | Tipo   | Descripción                                                                 |
|---------|--------|-----------------------------------------------------------------------------|
| actions | string | Pares "acción \| responsable" separados por punto y coma, o literal "No hay acciones identificadas" |

## Reglas (005)

- **Cuando hay acciones**: Cada par tiene formato `acción | responsable`. Pares separados por punto y coma (;). Ejemplo: `"Enviar informe antes del viernes | María; Revisar contrato | Por asignar"`.
- **Cuando no hay acciones identificables**: Literal `"No hay acciones identificadas"` (nunca cadena vacía).
- **Orden**: Por primera aparición de la acción en el texto de entrada.
- **Responsable no identificable**: Usar `"Por asignar"` (ej. acción sin atribución explícita, responsable solo por cargo).
- **Varios responsables**: Usar el primer nombre mencionado.
- **Acciones redundantes**: Consolidar en una, preferir la variante más específica.
- **Caracteres especiales**: Acción y responsable NO deben contener "|" ni ";"; reformular si el texto fuente los incluye.

## Ejemplos

| Texto de entrada                                                      | actions                                                               |
|-----------------------------------------------------------------------|-----------------------------------------------------------------------|
| "María enviará el informe antes del viernes"                          | `"Enviar informe antes del viernes \| María"`                         |
| "Se debe revisar el contrato"                                         | `"Revisar el contrato \| Por asignar"`                                |
| "María enviará el informe. Juan revisará el contrato."                | `"Enviar informe \| María; Revisar contrato \| Juan"`                 |
| "María y Pedro se encargarán del informe"                             | `"Enviar informe \| María"` (primer responsable)                      |
| "El gerente enviará el resumen"                                       | `"Enviar resumen \| Por asignar"` (cargo sin nombre)                  |
| "Reunión de brainstorming sin acuerdos"                               | `"No hay acciones identificadas"`                                     |
