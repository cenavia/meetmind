# Contract: Campo participants (respuesta de procesamiento)

**Feature**: 003-participants-extraction | **Aplica a**: `POST /api/v1/process/text`, `POST /api/v1/process/file`

---

## Formato

| Campo         | Tipo   | Descripción                                                                 |
|---------------|--------|-----------------------------------------------------------------------------|
| participants  | string | Nombres de participantes separados por coma, o literal "No identificados"   |

## Reglas (003)

- **Cuando hay participantes**: Lista de nombres separados por coma. Ejemplo: `"Juan Pérez, María López, Pedro García"`.
- **Cuando no hay participantes identificables**: Literal `"No identificados"` (nunca cadena vacía).
- **Orden**: Por primera aparición en el texto de entrada.
- **Deduplicación**: Cada persona aparece una sola vez; se prefiere la variante más completa del nombre.
- **Exclusiones**: No se incluyen términos genéricos ("persona", "alguien", "participante") ni títulos (Dr., Ing., Sr., etc.); solo nombre y apellido.

## Ejemplos

| Texto de entrada                               | participants                                   |
|-----------------------------------------------|------------------------------------------------|
| "Juan, María y Pedro asistieron..."           | `"Juan, María, Pedro"`                         |
| "Laura García propuso... Laura acordó..."     | `"Laura García"` (deduplicado, nombre completo)|
| "Se discutió el presupuesto..."               | `"No identificados"`                           |
| "El Dr. Pérez asistió..."                     | `"Pérez"` o `"Juan Pérez"` (sin título)        |
