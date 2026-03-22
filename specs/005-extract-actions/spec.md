# Feature Specification: Ver acciones acordadas con responsables

**Feature Branch**: `005-extract-actions`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: US-005 — Ver las acciones acordadas en la reunión con su responsable asignado para dar seguimiento a compromisos y trazabilidad

## Assumptions

- Existe un flujo de procesamiento previo que entrega texto transcrito o notas (US-000, US-001 o US-002).
- La extracción de acciones es un componente visible en la salida del sistema, consumido por Ricardo (líder) para trazabilidad y Pablo (desarrollador) para referencias de acuerdos técnicos.
- El formato de salida es "acción | responsable" para cada par; pares separados por punto y coma.
- Las acciones implícitas (compromisos inferibles del contexto) se incluyen cuando la inferencia es razonable; se evita inventar acciones sin evidencia textual.

## Clarifications

### Session 2026-03-21

- Q: ¿Separador entre pares acción-responsable? → A: Punto y coma (;) entre pares; pipe (|) entre acción y responsable dentro de cada par
- Q: ¿Qué mostrar cuando no hay acciones identificadas? → A: Siempre "No hay acciones identificadas" cuando hay 0 acciones (nunca cadena vacía)
- Q: ¿Incluir sección explícita "Out of Scope"? → A: Sí, añadir sección con límites explícitos
- Q: ¿Cómo representar la salida cuando una acción tiene varios responsables explícitos? → A: Usar el primer responsable mencionado en el texto
- Q: ¿Qué mostrar cuando el responsable se identifica solo por cargo (ej. "el gerente")? → A: Usar "Por asignar"
- Q: ¿En qué orden deben aparecer las acciones cuando hay múltiples? → A: Orden de primera aparición en el texto
- Q: Ante acciones claramente redundantes (misma acción, distintas redacciones), ¿qué criterio priorizar? → A: Consolidar; preferir la variante más específica (ej. con plazo o detalle)
- Q: ¿Cómo manejar cuando la acción o responsable incluyen "|" o ";"? → A: Reformular para evitar caracteres especiales en la salida

## Out of Scope

- Priorización o plazos de las acciones: no se extraen fechas límite ni prioridades; solo acción y responsable.
- Validación de que el responsable sea participante de la reunión: el sistema asigna el responsable mencionado en el texto aunque no esté en la lista de participantes; la consistencia se deja a iteraciones futuras.
- Jerarquías o subtareas: solo acciones de primer nivel; no se desglosan en subacciones.
- Límite de cantidad de acciones o optimización para textos muy largos: no hay límite explícito en esta feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver acciones con responsables explícitos (Priority: P1)

Como Ricardo o Pablo, quiero ver las acciones acordadas en la reunión con su responsable asignado cuando sea identificable en el texto, para dar seguimiento a compromisos y trazabilidad.

**Why this priority**: Es el requisito central de la feature; sin la extracción de acciones y la asociación con responsables no hay valor entregable.

**Independent Test**: Procesar un texto que diga "María enviará el informe antes del viernes" y verificar que la salida incluye "Enviar informe antes del viernes | María" con el formato acción | responsable.

**Acceptance Scenarios**:

1. **Given** el texto dice "María enviará el informe antes del viernes", **When** el sistema procesa el texto, **Then** la salida incluye "Enviar informe antes del viernes | María" con formato acción | responsable
2. **Given** el texto incluye variantes lingüísticas como "se encargará", "debe", "comprometió a", **When** el sistema extrae acciones, **Then** identifica el compromiso y el responsable asociado
3. **Given** el usuario visualiza la salida del procesamiento, **When** examina la sección de acciones, **Then** ve cada par como "acción | responsable"

---

### User Story 2 - Acciones sin responsable identificable (Priority: P1)

Como Ricardo o Pablo, quiero que cuando no se pueda determinar el responsable de una acción, el sistema muestre "Por asignar", para no inventar responsables y mantener la trazabilidad de la acción.

**Why this priority**: Garantiza transparencia y evita asignaciones incorrectas cuando el texto no lo permite.

**Independent Test**: Procesar un texto que diga "Se debe revisar el contrato" y verificar que la salida incluye "Revisar el contrato | Por asignar".

**Acceptance Scenarios**:

1. **Given** el texto dice "Se debe revisar el contrato", **When** el sistema procesa el texto, **Then** la salida incluye "Revisar el contrato | Por asignar"
2. **Given** una acción mencionada sin atribución explícita de responsable, **When** el sistema extrae acciones, **Then** asigna "Por asignar" como responsable
3. **Given** el texto no permite inferir quién es el responsable, **When** el sistema presenta la acción, **Then** nunca inventa un responsable; siempre usa "Por asignar"

---

### User Story 3 - Múltiples acciones con formato consistente (Priority: P2)

Como Ricardo o Pablo, quiero ver múltiples acciones extraídas con un formato consistente, para revisar de forma ordenada los compromisos de la reunión.

**Why this priority**: Garantiza usabilidad cuando hay varias acciones en la misma reunión.

**Independent Test**: Procesar un texto con varias acciones (explícitas e implícitas) y verificar que cada par acción-responsable está separado correctamente.

**Acceptance Scenarios**:

1. **Given** hay varias acciones en el texto, **When** el sistema extrae las acciones, **Then** cada par está separado por punto y coma (;), tiene formato "acción | responsable" y las acciones aparecen en orden de primera aparición en el texto
2. **Given** el texto incluye acciones implícitas inferibles, **When** el sistema extrae acciones, **Then** las incluye con la mejor estimación posible de responsable (o "Por asignar" si no es inferible)
3. **Given** la salida de múltiples acciones, **When** el usuario la examina, **Then** puede distinguir claramente cada acción y su responsable

---

### User Story 4 - Sin acciones identificables (Priority: P2)

Como Ricardo o Pablo, quiero que cuando el texto no contenga acciones acordadas identificables, el sistema indique claramente "No hay acciones identificadas", para no mostrar información inventada.

**Why this priority**: Mantiene coherencia con otras features (participantes, temas) y evita confusión.

**Independent Test**: Procesar un texto que no mencione compromisos ni acuerdos y verificar que la salida sea "No hay acciones identificadas".

**Acceptance Scenarios**:

1. **Given** el texto no menciona acciones ni compromisos, **When** el sistema procesa el texto, **Then** la salida es "No hay acciones identificadas"
2. **Given** el texto solo incluye discusiones sin acuerdos explícitos, **When** el sistema extrae acciones, **Then** no inventa acciones; devuelve "No hay acciones identificadas"

---

### Edge Cases

- ¿Qué ocurre cuando una acción menciona varios responsables (ej. "María y Pedro se encargarán de...")? El sistema DEBE usar el primer responsable mencionado en el texto como responsable de la acción.
- ¿Qué ocurre cuando el responsable se menciona solo por cargo (ej. "el gerente enviará...")? El sistema DEBE usar "Por asignar"; solo se consideran responsables cuando hay nombre propio explícito en el texto.
- ¿Qué ocurre cuando hay acciones solapadas o redundantes (ej. "Enviar informe" y "Entregar el informe antes del viernes")? El sistema DEBE consolidar cuando sea claramente la misma acción, prefiriendo la variante más específica (ej. con plazo o detalle); si hay duda, incluir ambas para no perder información.
- ¿Qué ocurre cuando no hay acciones identificables? La salida es "No hay acciones identificadas" (nunca cadena vacía).
- ¿Qué ocurre cuando la acción o el responsable incluyen "|" o ";"? El sistema DEBE reformular el texto de acción o responsable para evitar esos caracteres en la salida, preservando el significado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE extraer las acciones acordadas en la reunión a partir del texto transcrito o notas, identificando compromisos explícitos e implícitos
- **FR-002**: El sistema DEBE asociar un responsable a cada acción cuando sea identificable en el texto; cuando no sea posible, DEBE usar "Por asignar"
- **FR-003**: El sistema DEBE formatear cada par como "acción | responsable", con pares separados por punto y coma (;), en orden de primera aparición en el texto. Las acciones y responsables DEBEN reformularse para no contener "|" ni ";" cuando el texto fuente los incluya
- **FR-004**: El sistema DEBE incluir variantes lingüísticas de compromiso ("se encargará", "debe", "comprometió a", "acordó que", etc.) al identificar acciones
- **FR-005**: El sistema DEBE incluir acciones implícitas cuando sean razonablemente inferibles del contexto; no DEBE inventar acciones sin evidencia textual. Cuando haya acciones solapadas o redundantes claramente referidas a la misma acción, DEBE consolidar prefiriendo la variante más específica
- **FR-006**: Cuando no hay acciones identificables, el sistema DEBE devolver "No hay acciones identificadas" (nunca cadena vacía)
- **FR-007**: La salida de acciones DEBE estar visible en la respuesta del procesamiento para que el usuario la consulte

### Key Entities

- **Acción acordada**: Compromiso identificado en la reunión (explícito o implícito); representado como texto breve que describe la acción; asociada a un responsable cuando es identificable
- **Responsable**: Persona asignada a la acción; puede ser un nombre identificado en el texto o "Por asignar" cuando no es determinable
- **Par acción-responsable**: Estructura "acción | responsable"; múltiples pares separados por punto y coma, ordenados por primera aparición en el texto

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios ven las acciones acordadas con su responsable (o "Por asignar") en la salida del procesamiento en cada ejecución
- **SC-002**: El formato "acción | responsable" con separador punto y coma entre pares es consistente en todas las salidas
- **SC-003**: Cuando el texto menciona explícitamente un responsable para una acción, la asociación es correcta en al menos el 90% de los casos (verificable por revisión manual en conjunto de prueba)
- **SC-004**: Cuando no hay acciones identificables en el texto, la salida es consistentemente "No hay acciones identificadas", sin inventar acciones
