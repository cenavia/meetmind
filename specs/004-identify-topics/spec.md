# Feature Specification: Ver temas principales discutidos

**Feature Branch**: `004-identify-topics`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: US-004 — Ver temas principales discutidos en la reunión para entender el alcance de la discusión sin revisar todo el contenido

## Assumptions

- Existe un flujo de procesamiento previo que entrega texto transcrito o notas (US-000, US-001 o US-002).
- La visualización de temas principales es un componente visible en la salida del sistema, consumido por gerentes (Elena) y líderes (Ricardo) para captar rápidamente el alcance de la reunión.
- Los temas se presentan como lista de 3 a 5 elementos, separados por punto y coma; si hay menos datos identificables, se muestran los disponibles sin forzar relleno.
- La interfaz de usuario incluye flujos donde el usuario ingresa texto pegado o sube un archivo; durante el procesamiento es necesario mostrar retroalimentación visual.

## Clarifications

### Session 2026-03-21

- Q: ¿Qué mostrar cuando no hay temas identificados (0 temas)? → A: Siempre "No hay temas identificados" cuando hay 0 temas (nunca cadena vacía)
- Q: ¿Cómo manejar temas solapados (ej. "Presupuesto" y "Presupuesto Q2")? → A: Consolidar en un solo tema; preferir la variante más específica (ej. "Presupuesto Q2")
- Q: ¿En qué orden deben mostrarse los temas en la lista? → A: Orden de primera aparición en el texto
- Q: ¿Qué ocurre con el loader cuando el procesamiento falla (error, timeout)? → A: El loader se oculta y se muestra un mensaje de error claro al usuario
- Q: ¿Incluir sección explícita "Out of Scope"? → A: Sí, añadir sección con límites explícitos

## Out of Scope

- Jerarquías o categorías de temas: solo lista plana de temas; no se incluyen taxonomías ni relaciones entre temas.
- Priorización o ponderación de importancia: no se indica qué temas son más relevantes; todos se presentan al mismo nivel.
- Temas implícitos o inferidos sin evidencia clara en el texto: solo se extraen temas explícitos o claramente derivables del contenido.
- Límite de longitud de temas o optimización para textos muy largos (ej. >50.000 palabras): no hay límite explícito en esta feature; degradación con volúmenes extremos se abordará en iteraciones futuras.
- Cancelación explícita de procesamiento en curso: el comportamiento cuando el usuario cancela depende del flujo general; no está en alcance de esta feature.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver temas principales en reunión con múltiples temas (Priority: P1)

Como Elena o Ricardo, quiero ver entre 3 y 5 temas principales discutidos en la reunión, para entender el alcance de la discusión sin leer la minuta completa.

**Why this priority**: Es el requisito central de la feature; sin la identificación y visualización de temas principales no hay valor entregable.

**Independent Test**: Procesar un texto que discuta varios temas (presupuesto, plazos, recursos) y verificar que la salida incluye entre 3 y 5 temas con granularidad apropiada, separados por punto y coma.

**Acceptance Scenarios**:

1. **Given** el texto discute presupuesto, plazos y recursos, **When** el sistema procesa el texto, **Then** la salida incluye entre 3 y 5 temas
2. **Given** los temas extraídos, **When** el usuario los examina, **Then** cada tema tiene nivel de granularidad apropiado (ni muy general ni muy específico)
3. **Given** la salida de temas, **When** se presenta al usuario, **Then** los temas están separados por punto y coma, en orden de primera aparición en el texto

---

### User Story 2 - Reunión breve con pocos temas (Priority: P2)

Como Elena o Ricardo, quiero que cuando el texto solo mencione pocos temas concretos, el sistema retorne únicamente los identificados sin inventar o forzar relleno, para confiar en la información mostrada.

**Why this priority**: Garantiza transparencia y evita mostrar información inventada cuando no hay suficientes datos.

**Independent Test**: Procesar un texto que mencione solo 2 temas concretos y verificar que la salida contiene exactamente esos 2 temas, sin temas adicionales inventados.

**Acceptance Scenarios**:

1. **Given** el texto solo menciona 2 temas concretos, **When** el sistema procesa el texto, **Then** retorna los 2 temas identificados
2. **Given** hay menos de 3 temas identificables, **When** el sistema extrae temas, **Then** no fuerza relleno con temas inventados
3. **Given** no se identifica ningún tema (0 temas), **When** el sistema procesa el texto, **Then** la salida es "No hay temas identificados" (nunca cadena vacía)

---

### User Story 3 - Evitar temas genéricos y priorizar granularidad (Priority: P3)

Como Elena o Ricardo, quiero que el sistema evite temas demasiado genéricos (ej. "Reunión de trabajo") y priorice temas específicos del contenido (ej. "Sprint 12", "Módulo de facturación"), para obtener una visión útil del alcance.

**Why this priority**: Mejora la calidad de la extracción y la utilidad de la vista rápida para los gerentes.

**Independent Test**: Procesar texto que mencione temas específicos y verificables, y comprobar que no se incluyen temas genéricos como "Reunión" o "Discusión general".

**Acceptance Scenarios**:

1. **Given** el texto habla de "revisión del sprint 12 y bugs del módulo de facturación", **When** el sistema extrae temas, **Then** evita "Reunión de trabajo" como tema
2. **Given** el contenido es específico, **When** se generan los temas, **Then** incluye temas concretos como "Sprint 12" y "Módulo de facturación"
3. **Given** el texto menciona "Presupuesto" y "Presupuesto Q2" como temas relacionados, **When** el sistema extrae temas, **Then** consolida en un solo tema, mostrando la variante más específica ("Presupuesto Q2")

---

### User Story 4 - Indicador de carga durante el análisis (Priority: P1)

Como Elena o Ricardo, quiero ver un indicador de carga (loader) visible mientras el sistema analiza el texto pegado o el archivo subido, para saber que el proceso está en curso y obtener retroalimentación inmediata.

**Why this priority**: Esencial para la experiencia de usuario; sin feedback visual durante el procesamiento, el usuario puede asumir que la aplicación no responde.

**Independent Test**: Ingresar texto o subir un archivo e iniciar el procesamiento; verificar que aparece un loader visible hasta que finalice el análisis.

**Acceptance Scenarios**:

1. **Given** el usuario ha ingresado texto o subido un archivo, **When** el sistema está procesando y analizando el contenido, **Then** la interfaz muestra un indicador de carga
2. **Given** el procesamiento está en curso, **When** el usuario observa la pantalla, **Then** el loader permanece visible hasta que el análisis finalice
3. **Given** ocurre un error durante el procesamiento (red, timeout), **When** el sistema detecta el fallo, **Then** el loader se oculta y se muestra un mensaje de error claro al usuario

---

### Edge Cases

- ¿Qué ocurre cuando no se identifica ningún tema (0 temas)? El sistema devuelve "No hay temas identificados"; nunca cadena vacía.
- ¿Qué ocurre cuando el texto menciona temas solapados (ej. "Presupuesto" y "Presupuesto Q2")? El sistema consolida en un solo tema, prefiriendo la variante más específica.
- ¿Qué ocurre cuando el texto discute solo un tema? Se retorna ese único tema; no se fuerza relleno con temas adicionales inventados.
- ¿Qué ocurre cuando el texto es demasiado genérico o abstracto (ej. "Reunión de coordinación")? Se extraen los temas identificables; si no hay temas con granularidad suficiente, se retorna lo disponible; si hay 0 temas, se muestra "No hay temas identificados". El sistema evita incluir temas genéricos por diseño.
- ¿Qué ocurre cuando el procesamiento falla (error de red, timeout, etc.)? El loader se oculta y se muestra un mensaje de error claro al usuario para que pueda reintentar.
- ¿Qué ocurre si el usuario cambia de texto o archivo mientras hay procesamiento en curso? Comportamiento depende del diseño del flujo general (cancelación, cola); asumir que el loader refleja el estado del procesamiento actual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE identificar entre 3 y 5 temas principales discutidos en la reunión a partir del texto transcrito o notas
- **FR-002**: Los temas DEBEN tener nivel de granularidad apropiado (ni muy general ni muy específico); el sistema DEBE evitar temas genéricos como "Reunión" o "Discusión general"; cuando hay temas solapados (ej. "Presupuesto" y "Presupuesto Q2"), DEBE consolidar en un solo tema preferiendo la variante más específica
- **FR-003**: Los temas DEBEN presentarse separados por punto y coma, en orden de primera aparición en el texto
- **FR-004**: Cuando hay menos de 3 temas identificables, el sistema DEBE retornar los disponibles sin forzar relleno con temas inventados; cuando no hay temas (0), DEBE devolver "No hay temas identificados" (nunca cadena vacía)
- **FR-005**: La interfaz de usuario DEBE mostrar un indicador de carga visible mientras se analiza el texto pegado o el archivo subido
- **FR-006**: El indicador de carga DEBE permanecer visible hasta que el análisis finalice; cuando ocurre un error (red, timeout, etc.), DEBE ocultarse y mostrarse un mensaje de error claro al usuario
- **FR-007**: La salida de temas DEBE estar visible en la respuesta del procesamiento para que el usuario la consulte

### Key Entities

- **Tema principal**: Tema discutido en la reunión con nivel de granularidad apropiado; no genérico ni demasiado específico; representado como texto corto; cuando hay variantes solapadas del mismo concepto, se consolida en la más específica (ej. "Presupuesto Q2" en lugar de "Presupuesto" y "Presupuesto Q2")
- **Lista de temas**: Salida estructurada que contiene entre 1 y 5 temas separados por punto y coma, ordenados por primera aparición en el texto; si hay menos de 3 identificables, se muestran los disponibles; cuando hay 0 temas, el valor es "No hay temas identificados" (nunca cadena vacía); nunca se inventan temas para rellenar

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios ven entre 3 y 5 temas principales (o los disponibles si hay menos) en la salida del procesamiento en cada ejecución
- **SC-002**: Los temas presentados tienen granularidad apropiada; temas genéricos como "Reunión de trabajo" no aparecen en la lista (verificable por revisión manual en conjunto de prueba)
- **SC-003**: Cuando hay menos de 3 temas identificables, la salida contiene solo los temas reales; no se inventan temas adicionales
- **SC-004**: Durante el procesamiento de texto o archivo, los usuarios ven un indicador de carga visible hasta que el análisis finalice
