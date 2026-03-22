# Feature Specification: Ver extracción de participantes

**Feature Branch**: `003-participants-extraction`  
**Created**: 2025-03-21  
**Status**: Draft  
**Input**: US-003 — Ver lista de participantes identificados en la reunión a partir del texto transcrito o notas

## Assumptions

- Existe un flujo de procesamiento previo que entrega texto transcrito o notas (US-000, US-001 o US-002).
- La extracción de participantes es un componente visible en la salida del sistema, consumido por líderes de proyecto como Ricardo para asignar responsabilidades.
- El formato de salida de participantes es una lista de nombres separados por comas; no se requieren estructuras jerárquicas ni roles en esta feature.

## Clarifications

### Session 2025-03-21

- Q: ¿Cuándo debe devolverse "No identificados" vs lista vacía cuando no hay participantes? → A: Siempre "No identificados" cuando no hay participantes (nunca cadena vacía)
- Q: Si la misma persona se menciona con variantes (ej. "Juan Pérez" y "Juan"), ¿una o varias entradas? → A: Una entrada por participante (deduplicar); preferir variante más completa (nombre completo)
- Q: ¿En qué orden deben aparecer los participantes en la lista? → A: Orden de primera aparición en el texto
- Q: Si el texto incluye títulos (ej. "Dr. García", "Ing. López"), ¿incluirlos en la lista? → A: Excluir títulos; solo nombre y apellido
- Q: ¿Incluir sección explícita "Out of Scope"? → A: Sí, añadir sección con límites explícitos

## Out of Scope

- Filtrar nombres ficticios o de personajes: el sistema extrae todos los nombres presentes; la interpretación de si son reales o ficticios corresponde al usuario.
- Estructuras jerárquicas o roles de participantes: no se incluyen cargos, roles ni relaciones entre participantes; solo lista plana de nombres.
- Incluir participantes mencionados solo por cargo (ej. "el gerente", "el líder técnico"): fuera de alcance; solo nombres propios explícitos.
- Límite de participantes o optimización para volúmenes muy altos (ej. >20): no hay límite en esta feature; degradación con volúmenes extremos se abordará en iteraciones futuras.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver participantes identificados en reunión (Priority: P1)

Como Ricardo (líder de proyecto), quiero ver la lista de participantes identificados en la reunión, para saber quién estuvo presente y poder asignar responsabilidades.

**Why this priority**: Es el requisito central de la feature; sin la extracción y visualización de participantes no hay valor entregable.

**Independent Test**: Procesar un texto que mencione nombres concretos y verificar que la lista de participantes se muestra correctamente, excluyendo términos genéricos.

**Acceptance Scenarios**:

1. **Given** el texto menciona "Juan, María y Pedro asistieron a la reunión", **When** el sistema procesa el texto, **Then** la lista de participantes incluye Juan, María y Pedro
2. **Given** el texto incluye referencias como "persona" o "alguien", **When** el sistema extrae participantes, **Then** no se incluyen esos términos genéricos en la lista
3. **Given** el usuario visualiza la salida del procesamiento, **When** examina la sección de participantes, **Then** ve los nombres como lista separada por comas

---

### User Story 2 - Texto sin participantes identificables (Priority: P2)

Como Ricardo, quiero que cuando el texto no mencione nombres concretos, el sistema indique claramente que no se identificaron participantes, para no asumir datos inexistentes.

**Why this priority**: Garantiza transparencia y evita mostrar información inventada o engañosa cuando no hay datos suficientes.

**Independent Test**: Procesar un texto que no mencione nombres de personas y verificar que la salida sea "No identificados".

**Acceptance Scenarios**:

1. **Given** el texto no menciona nombres concretos de personas, **When** el sistema procesa el texto, **Then** la salida de participantes es "No identificados"
2. **Given** el texto solo incluye referencias impersonales ("se discutió...", "hubo acuerdo..."), **When** el sistema extrae participantes, **Then** no inventa nombres; devuelve "No identificados"

---

### User Story 3 - Participantes con apellidos y variantes (Priority: P3)

Como Ricardo, quiero que el sistema maneje correctamente nombres con apellidos y variantes (ej. "Juan Pérez" vs "Juan"), para tener una lista coherente y usable.

**Why this priority**: Mejora la calidad de la extracción en reuniones donde los participantes se mencionan de distintas formas.

**Independent Test**: Procesar texto que mencione a una misma persona con nombre completo y abreviado, y verificar coherencia en la salida.

**Acceptance Scenarios**:

1. **Given** el texto menciona "Laura García propuso..." y más adelante "Laura acordó...", **When** el sistema extrae participantes, **Then** la lista incluye a Laura García una sola vez (deduplicada), preferiblemente con nombre completo
2. **Given** hay abreviaturas o variantes de un mismo nombre, **When** se genera la lista de participantes, **Then** cada persona aparece una sola vez, con la variante más completa disponible

---

### Edge Cases

- ¿Qué ocurre cuando el texto menciona nombres ficticios o de personajes? El sistema extrae nombres presentes en el contexto; la interpretación de si son reales o ficticios corresponde al usuario. Si se requiere filtrar por tipo de mención, queda fuera de alcance en esta feature.
- ¿Qué ocurre cuando un participante se menciona solo por cargo (ej. "el gerente", "el líder técnico")? No se incluye en la lista de participantes; solo se incluyen nombres propios explícitos.
- ¿Qué ocurre cuando el nombre incluye título (ej. "Dr. García", "Ing. López")? Se excluye el título; la lista muestra solo nombre y apellido (ej. "García", "López" o nombre completo sin título).
- ¿Qué ocurre cuando hay muchos participantes (ej. >20)? La lista se presenta completa; no hay límite explícito en esta feature. Si el rendimiento o la usabilidad se degradan con volúmenes muy altos, se abordará en iteraciones futuras.
- ¿Qué ocurre con nombres en otros idiomas o escrituras? El sistema debe intentar conservar los nombres tal como aparecen en el texto; no se normaliza a un idioma específico.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE extraer e identificar los nombres de las personas que participaron en la reunión a partir del texto transcrito o notas
- **FR-002**: El sistema DEBE excluir términos genéricos ("persona", "alguien", "un participante") y títulos/honoríficos (Dr., Ing., Sr., etc.) de la lista de participantes; mostrar solo nombre y apellido
- **FR-003**: El sistema DEBE presentar la lista de participantes como nombres separados por comas, en orden de primera aparición en el texto
- **FR-004**: Cuando no hay participantes identificables, el sistema DEBE devolver el texto "No identificados" (nunca cadena vacía)
- **FR-005**: El sistema DEBE deduplicar participantes; cada persona aparece una sola vez en la lista
- **FR-006**: El sistema DEBE preferir la variante más completa del nombre cuando existan múltiples menciones (ej. "Juan Pérez" sobre "Juan")
- **FR-007**: La salida de participantes DEBE estar visible en la respuesta del procesamiento para que el usuario la consulte

### Key Entities

- **Participante**: Persona identificada por nombre propio que participó en la reunión; atributos: nombre (variante más completa cuando existan múltiples menciones); cada persona aparece una sola vez en la lista (deduplicación)
- **Lista de participantes**: Salida estructurada que contiene cero o más nombres separados por comas, ordenados por primera aparición en el texto; cuando no hay participantes identificables, el valor es siempre "No identificados" (nunca cadena vacía)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios ven la lista de participantes extraída en la salida del procesamiento en cada ejecución
- **SC-002**: Cuando el texto contiene nombres explícitos, al menos el 90% de los nombres mencionados correctamente se incluyen en la lista (medible por revisión manual en conjunto de prueba representativo)
- **SC-003**: Los términos genéricos ("persona", "alguien", "participante") no aparecen en la lista de participantes en ningún caso
- **SC-004**: Cuando no hay nombres identificables en el texto, la salida es consistentemente "No identificados", sin inventar nombres
