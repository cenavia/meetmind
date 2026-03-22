# Feature Specification: Ver minuta formal

**Feature Branch**: `006-generate-minutes`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: US-006 — Obtener una minuta formal estructurada de la reunión para compartir documentación profesional con stakeholders

## Clarifications

### Session 2026-03-21

- Q: ¿Cuál debe ser la salida exacta cuando no hay participantes, temas ni acciones extraídos? → A: Mensaje fijo estándar breve (ej.: "Minuta: No se identificó información procesable en la reunión.")
- Q: ¿Cómo debe organizarse la minuta cuando sí hay datos? → A: Texto narrativo continuo (párrafos fluidos integrando participantes, temas y acciones)
- Q: ¿Cómo se debe definir y validar el conteo de palabras? → A: Split por espacios (secuencias de caracteres separadas por espacios en blanco)
- Q: ¿Qué debe quedar explícitamente fuera de alcance en esta feature? → A: Solo generación de texto plano; sin exportar (PDF, DOCX, etc.), sin edición integrada, sin plantillas personalizables
- Q: ¿En qué idioma debe generarse la minuta? → A: Siempre español

## Assumptions

- Existe un flujo de procesamiento previo que entrega participantes, temas identificados y acciones extraídas (US-003, US-004, US-005).
- La minuta es el artefacto principal que Marina comparte con el equipo y Ricardo usa para auditoría.
- El límite de 150 palabras permite concisión manteniendo la esencia de la reunión; si la salida excede el límite, se aplica truncamiento o resumen conservando coherencia.
- La minuta se genera únicamente a partir de la información ya extraída; no se hace nueva extracción en este paso.

## Out of Scope

- Exportación a otros formatos (PDF, DOCX, etc.): la feature entrega solo texto plano.
- Edición integrada de la minuta: el usuario puede copiar/pegar en su herramienta preferida, pero no hay editor en el sistema.
- Plantillas personalizables: el formato es fijo (texto narrativo continuo, tono profesional formal).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Minuta completa con participantes, temas y acciones (Priority: P1)

Como Marina o Ricardo, quiero obtener una minuta formal de la reunión que integre participantes, temas y acciones cuando existan, para compartir documentación profesional con stakeholders.

**Why this priority**: Es el flujo principal; la minuta es el artefacto central que ambos usuarios necesitan para distribución y auditoría.

**Independent Test**: Dado un conjunto de participantes, temas y acciones ya extraídos, verificar que la salida es una minuta coherente de máximo 150 palabras, tono profesional y que incluye la información disponible.

**Acceptance Scenarios**:

1. **Given** existen participantes, temas y acciones extraídos, **When** el sistema genera la minuta, **Then** la minuta tiene máximo 150 palabras
2. **Given** existen participantes, temas y acciones extraídos, **When** el sistema genera la minuta, **Then** la minuta usa tono profesional y estructura formal
3. **Given** existen participantes, temas y acciones extraídos, **When** el usuario recibe la minuta, **Then** puede compartirla como documentación profesional con stakeholders
4. **Given** la minuta generada, **When** el usuario la lee, **Then** es legible y coherente con el contenido original de la reunión

---

### User Story 2 - Minuta con información parcial (Priority: P1)

Como Marina o Ricardo, quiero que cuando solo exista información parcial (por ejemplo solo temas, sin participantes ni acciones), el sistema genere una minuta que integre lo disponible manteniendo coherencia y legibilidad.

**Why this priority**: Garantiza que la feature aporte valor aunque no todas las extracciones previas hayan producido datos.

**Independent Test**: Dado solo temas identificados (sin participantes ni acciones), verificar que la minuta se genera integrando la información disponible y manteniendo coherencia.

**Acceptance Scenarios**:

1. **Given** solo se identificaron temas (sin participantes ni acciones), **When** el sistema genera la minuta, **Then** la minuta integra la información disponible
2. **Given** información parcial de cualquier tipo, **When** el sistema genera la minuta, **Then** mantiene coherencia y legibilidad
3. **Given** la minuta con información parcial, **When** el usuario la revisa, **Then** no contiene secciones inventadas ni información no presente en la entrada

---

### User Story 3 - Respeto del límite de extensión (Priority: P2)

Como Marina o Ricardo, quiero que la minuta tenga como máximo 150 palabras, para facilitar su lectura rápida y distribución por canales breves.

**Why this priority**: El límite de palabras es un requisito explícito de la US y afecta la usabilidad del artefacto.

**Independent Test**: Generar minuta con diferentes volúmenes de datos de entrada y verificar que la salida nunca supera 150 palabras.

**Acceptance Scenarios**:

1. **Given** cualquier entrada válida, **When** el sistema genera la minuta, **Then** el texto resultante tiene máximo 150 palabras
2. **Given** una minuta generada, **When** se cuenta el número de palabras, **Then** cumple la restricción sin excepción

---

### Edge Cases

- ¿Qué ocurre cuando no hay participantes, temas ni acciones extraídos? El sistema debe devolver un mensaje fijo estándar breve, por ejemplo: "Minuta: No se identificó información procesable en la reunión." (siempre ≤150 palabras, nunca cadena vacía).
- ¿Cómo se maneja texto que excede 150 palabras en la generación? Se aplica truncamiento o condensación preservando coherencia y priorizando participantes, temas y acciones más relevantes. Conteo de palabras: split por espacios en blanco.
- ¿Qué hacer si la información de entrada contiene caracteres especiales o formato inconsistente? La minuta debe ser legible y sin errores de formato que impidan su uso profesional.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE generar una minuta formal a partir de la información de participantes, temas y acciones ya extraída.
- **FR-002**: La minuta DEBE tener un máximo de 150 palabras (conteo: split por espacios en blanco; secuencias de caracteres entre espacios cuentan como una palabra).
- **FR-003**: La minuta DEBE usar tono profesional y estructura formal; se presentará como texto narrativo continuo (párrafos fluidos) integrando participantes, temas y acciones, sin secciones con encabezados explícitos. Siempre en español.
- **FR-004**: La minuta DEBE integrar de forma coherente los participantes, temas y acciones disponibles (incluyendo cuando solo parte de la información existe).
- **FR-005**: La minuta DEBE ser legible y coherente con el contenido original de la reunión.
- **FR-006**: El sistema DEBE manejar el caso en que la información de entrada sea parcial (por ejemplo solo temas) sin generar secciones inventadas.
- **FR-007**: Cuando no haya participantes, temas ni acciones extraídos, el sistema DEBE devolver un mensaje fijo estándar breve (ej.: "Minuta: No se identificó información procesable en la reunión."), nunca cadena vacía.

### Key Entities

- **Minuta**: Artefacto de texto formal en español que resume la reunión. Texto narrativo continuo (párrafos fluidos) que integra participantes, temas discutidos y acciones acordadas. Máximo 150 palabras (conteo: split por espacios). Se comparte con stakeholders para documentación y auditoría.
- **Información de entrada**: Agregado de participantes (US-003), temas (US-004) y acciones (US-005) ya extraídos en pasos previos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Marina y Ricardo pueden obtener una minuta lista para compartir en un único paso, sin edición manual, cuando la información previa está disponible.
- **SC-002**: El 100 % de las minutas generadas cumplen el límite de 150 palabras.
- **SC-003**: Las minutas son utilizables como documentación profesional (sin errores de formato, tono adecuado, coherencia con la reunión).
- **SC-004**: En escenarios con información parcial, la minuta sigue siendo coherente y no introduce información inexistente.
