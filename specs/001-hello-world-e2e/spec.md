# Feature Specification: Estructura inicial y Hello World end-to-end

**Feature Branch**: `001-hello-world-e2e`  
**Created**: 2025-03-21  
**Status**: Draft  
**Input**: US-000 — Estructura inicial del proyecto MeetMind y flujo mínimo end-to-end funcional

## Clarifications

### Session 2025-03-21

- Q: ¿Cómo debe comportarse el sistema cuando el usuario envía texto vacío (string vacío o solo espacios)? → A: Validación en UI — la UI impide enviar texto vacío (botón deshabilitado o mensaje antes de llamar a la API)
- Q: ¿Cómo debe invocar la UI al procesamiento en esta fase Hello World? → A: Vía API (HTTP) — la UI hace requests HTTP a la API, que invoca el grafo; validación completa de capas
- Q: ¿Cómo debe comportarse el sistema con textos muy largos (p. ej. >10.000 caracteres)? → A: Límite razonable (ej. 50.000 caracteres); rechazar con 400 y mensaje claro si se excede
- Q: ¿Debe la UI mostrar un estado de carga visible mientras procesa la solicitud? → A: Sí, obligatorio — spinner, texto "Procesando..." o deshabilitar botón hasta recibir respuesta
- Q: ¿Cómo debe obtener la UI la URL base de la API? → A: Variable de entorno (ej. API_BASE_URL) con valor por defecto http://localhost:8000

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verificar que el servicio API está operativo (Priority: P1)

Como desarrollador o Tech Lead, quiero comprobar que el servicio backend responde correctamente antes de ejecutar flujos más complejos, para confirmar que el entorno está correctamente configurado.

**Why this priority**: Sin un endpoint de salud funcional, no se puede validar el setup ni depurar problemas de infraestructura.

**Independent Test**: Se puede verificar completamente haciendo una solicitud al endpoint de salud y comprobando que devuelve indicación de servicio operativo con código de éxito.

**Acceptance Scenarios**:

1. **Given** el servidor está en ejecución, **When** se realiza una solicitud al endpoint de salud, **Then** se recibe código 200 y el cuerpo indica que el servicio está operativo
2. **Given** el servidor no está levantado, **When** se realiza la solicitud, **Then** la conexión falla o se recibe un error (comportamiento esperado)

---

### User Story 2 - Procesar texto vía API y recibir salida estructurada (Priority: P2)

Como desarrollador, quiero enviar texto de reunión a la API y recibir una respuesta estructurada con participantes, temas, acciones, minuta y resumen, para validar que el flujo de procesamiento funciona correctamente.

**Why this priority**: Es el núcleo del valor del sistema; sin este flujo, no hay funcionalidad de procesamiento.

**Independent Test**: Se puede probar enviando un POST con JSON `{"text": "..."}` y verificando que la respuesta incluye los campos esperados (participantes, temas, acciones, minuta, resumen).

**Acceptance Scenarios**:

1. **Given** la API está ejecutándose, **When** envío POST con JSON `{"text": "Reunión con Juan y María. Discutimos el presupuesto."}`, **Then** recibo código 200
2. **Given** la respuesta anterior, **When** examino el cuerpo, **Then** incluye al menos: participantes, temas, acciones, minuta, resumen (en formato estructurado acordado)
3. **Given** el input está vacío, **When** el usuario intenta procesar, **Then** la UI impide el envío (botón deshabilitado o mensaje de validación) y no se invoca la API

---

### User Story 3 - Flujo completo desde la interfaz de usuario (Priority: P3)

Como usuario del sistema (o desarrollador validando el flujo E2E), quiero escribir texto en la interfaz, pulsar un botón de procesamiento y ver el resultado estructurado en pantalla, para confirmar que todo el flujo usuario → API → procesamiento → visualización funciona.

**Why this priority**: Valida la integración entre capas; depende de P1 y P2.

**Independent Test**: Se ejecuta la API y la UI (con API como backend), se introduce texto, se pulsa "Procesar" y se comprueba que el resultado devuelto por la API aparece formateado en la interfaz.

**Acceptance Scenarios**:

1. **Given** la API y la UI están ejecutándose, **When** escribo "Reunión de prueba con Juan" en el input y pulso "Procesar", **Then** aparece estado de carga visible durante el procesamiento, **And** luego veo el resultado estructurado (participantes, temas, acciones, minuta, resumen) en la interfaz
2. **Given** la misma configuración, **When** la API no está disponible, **Then** la UI muestra un mensaje de error o estado de fallo apropiado (no fallo silencioso)
3. **Given** la documentación de ejecución, **When** un nuevo desarrollador sigue las instrucciones, **Then** puede ejecutar el flujo completo en menos de 10 minutos

---

### Edge Cases

- ¿Qué ocurre cuando el texto de entrada está vacío? La UI impide enviar (botón deshabilitado o mensaje de validación antes de invocar la API); no se realiza la llamada.
- ¿Qué ocurre cuando la API no responde (timeout, caída)? La UI debe informar al usuario sin fallar de forma críptica.
- ¿Qué ocurre si las dependencias no están instaladas? Las instrucciones deben ser suficientes para reproducir el entorno.
- ¿Qué ocurre con caracteres especiales o textos muy largos? Límite de longitud (ej. 50.000 caracteres); si se excede, la API rechaza con 400 y mensaje claro. Caracteres especiales: aceptados según codificación estándar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE exponer un endpoint de salud que responda con código de éxito e indique operatividad
- **FR-002**: El sistema DEBE aceptar texto plano como entrada vía un endpoint de procesamiento; DEBE rechazar con error 400 y mensaje claro si el texto excede el límite de longitud definido (ej. 50.000 caracteres)
- **FR-003**: El sistema DEBE devolver una respuesta estructurada que incluya: participantes, temas, acciones, minuta y resumen
- **FR-004**: El sistema DEBE proporcionar una interfaz de usuario con campo de texto y botón de procesamiento; la UI DEBE impedir enviar texto vacío (botón deshabilitado o mensaje de validación)
- **FR-005**: La interfaz DEBE invocar el flujo de procesamiento vía API (HTTP): la UI hace requests a la API (URL obtenida de variable de entorno, ej. `API_BASE_URL` con default `http://localhost:8000`), que invoca el grafo; la UI muestra el resultado devuelto
- **FR-009**: La UI DEBE mostrar estado de carga visible durante el procesamiento (spinner, texto "Procesando..." o botón deshabilitado) hasta recibir respuesta
- **FR-006**: El sistema DEBE estar documentado con instrucciones claras de instalación y ejecución para reproducibilidad; la documentación DEBE incluir la variable de entorno para la URL base de la API (ej. `API_BASE_URL`, default `http://localhost:8000`)
- **FR-007**: La estructura de directorios DEBE reflejar la separación en capas (API, lógica de negocio, UI)
- **FR-008**: Las dependencias DEBE estar gestionadas de forma reproducible (archivo de dependencias y comando de instalación estándar)

### Key Entities

- **Participante**: Persona mencionada o identificada en la reunión
- **Tema**: Asunto o punto tratado en la reunión
- **Acción**: Tarea o compromiso derivado, con posible responsable
- **Minuta**: Resumen narrativo estructurado de lo tratado
- **Resumen**: Síntesis ejecutiva de la reunión

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un desarrollador nuevo puede seguir la documentación y ejecutar el flujo completo (API + UI + procesamiento de texto) en menos de 15 minutos
- **SC-002**: El endpoint de salud responde en menos de 2 segundos en condiciones normales
- **SC-003**: El procesamiento de texto de prueba (<500 caracteres) devuelve respuesta estructurada en menos de 5 segundos (modo mock/demo)
- **SC-004**: El 100% de los criterios de aceptación de las User Stories P1, P2 y P3 son verificables manualmente
- **SC-005**: La estructura de proyecto es reproducible: otro desarrollador puede clonar, instalar dependencias y ejecutar sin pasos adicionales no documentados
