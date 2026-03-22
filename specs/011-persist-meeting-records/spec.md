# Feature Specification: Almacenamiento persistente de reuniones procesadas

**Feature Branch**: `011-persist-meeting-records`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Persistir reuniones procesadas de forma durable: identificador único, resultados (participantes, temas, acciones, minuta, resumen), metadatos de archivo, estado y errores de procesamiento; operaciones crear al finalizar, obtener por id y listar; datos disponibles tras reinicio. Origen: US-012."

## Clarifications

### Session 2026-03-22

- Q: ¿Qué frontera de confianza y acceso aplican a consultar registros persistidos (get/list)? → A: Entorno de confianza; sin autenticación ni autorización explícita para get y list en este entregable (opción A).
- Q: ¿Retención máxima, borrado automático o eliminación bajo demanda en producto? → A: No exigidos en este entregable; la retención práctica y purgas las define despliegue u operación (opción A).
- Q: Si el mismo archivo o contenido se procesa más de una vez, ¿cuántos registros persistidos debe haber? → A: Cada finalización crea un registro nuevo con identificador nuevo; no fusión ni sustitución automática (opción B).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guardar reunión al terminar el procesamiento (Priority: P1)

Cuando una **ejecución** del flujo de procesamiento de una reunión finaliza, el producto debe conservar de forma durable un registro que represente **esa ejecución** y su resultado, de modo que no dependa de la memoria de la sesión actual.

**Why this priority**: Sin persistencia no hay trazabilidad ni base para consultas posteriores (p. ej. historial); es el núcleo de la capacidad.

**Independent Test**: Tras un procesamiento que llega a su fin, existe un identificador estable y los datos acordados quedan almacenados y verificables sin depender de la interfaz en curso.

**Acceptance Scenarios**:

1. **Given** que el procesamiento de una reunión concluyó con éxito, **When** se finaliza el procesamiento, **Then** se crea un registro con un identificador único e inmutable y se guardan participantes, temas, acciones, minuta y resumen.
2. **Given** que el procesamiento terminó, **When** se revisa el registro creado, **Then** el estado refleja el resultado del procesamiento (completado, fallido o parcial), existe una marca de tiempo de creación y, si hubo advertencias o fallos, quedan registrados en el campo de errores o advertencias de procesamiento.
3. **Given** que hubo un archivo de origen identificable, **When** se guarda el registro, **Then** se conservan el nombre y el tipo de ese archivo cuando estén disponibles.

---

### User Story 2 - Consultar una reunión por su identificador (Priority: P2)

Quien use el producto (o un proceso asociado) debe poder recuperar el registro completo de una reunión guardada a partir de su identificador único.

**Why this priority**: La consulta puntual habilita trazabilidad y verificación de lo almacenado frente a lo esperado.

**Independent Test**: Con un identificador conocido de una reunión ya guardada, la consulta devuelve el mismo contenido que fue persistido.

**Acceptance Scenarios**:

1. **Given** que existe una reunión guardada con un identificador conocido, **When** se solicita esa reunión por identificador, **Then** se obtiene el registro completo y los datos coinciden con lo guardado.
2. **Given** que no existe reunión para un identificador dado, **When** se solicita por ese identificador, **Then** el resultado es inequívoco (p. ej. indicación clara de no encontrado) y no se devuelven datos de otra reunión.

---

### User Story 3 - Listar reuniones guardadas (Priority: P2)

Debe poder obtenerse el conjunto de reuniones almacenadas de forma ordenada y predecible para apoyar vistas de historial o auditoría básica.

**Why this priority**: El listado ordenado permite revisar lo procesado recientemente y prepara funciones de historial sin depender de memoria volátil.

**Independent Test**: Con varias reuniones ya guardadas, el listado incluye todas y respeta un criterio de orden explícito.

**Acceptance Scenarios**:

1. **Given** que existen varias reuniones guardadas, **When** se solicita el listado, **Then** se reciben todas las reuniones almacenadas en el sistema de persistencia.
2. **Given** el mismo conjunto de reuniones, **When** se solicita el listado, **Then** el orden es por fecha de creación, de la más reciente a la más antigua.

---

### Edge Cases

- Procesamiento que termina en estado parcial o fallido: el registro debe persistirse igualmente con el estado y mensajes de error o advertencia correspondientes cuando aplique.
- Identificador inexistente en consulta por id: respuesta clara sin filtración de datos ajenos.
- Ninguna reunión almacenada: el listado es vacío y coherente (sin errores confusos).
- Metadatos de archivo de origen ausentes: el registro se guarda sin bloquear el resto de campos obligatorios.
- Reinicio del producto o del entorno de ejecución: los registros previos permanecen accionables mediante consulta por id y listado.
- Exposición de las consultas fuera de un entorno de confianza (p. ej. Internet abierto sin controles perimetrales) queda fuera del alcance de esta especificación; se asume que quien despliega acota el acceso acorde a este supuesto.
- Misma entrada o archivo procesado en varias ocasiones: cada finalización válida produce un **registro distinto** con su propio identificador; el listado puede mostrar varias entradas aparentemente “duplicadas” en contenido o nombre de archivo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El producto DEBE crear un registro de reunión procesada al finalizar el procesamiento (éxito, fallo o resultado parcial según corresponda).
- **FR-002**: Cada registro DEBE tener un identificador único e inmutable asignado en el momento de la creación.
- **FR-003**: Cada registro DEBE almacenar: participantes, temas, acciones, minuta, resumen ejecutivo, estado del procesamiento, marca de tiempo de creación y errores o advertencias de procesamiento cuando existan.
- **FR-004**: El estado DEBE ser uno de: completado, fallido o parcial, de forma consistente en todo el producto.
- **FR-005**: Cuando exista archivo de origen identificable, el registro DEBE poder incluir al menos el nombre y el tipo de dicho archivo; si no hay archivo de origen, esos metadatos pueden quedar vacíos.
- **FR-006**: El producto DEBE permitir recuperar un registro completo por su identificador.
- **FR-007**: El producto DEBE permitir listar todos los registros de reuniones almacenados, ordenados por fecha de creación de la más reciente a la más antigua.
- **FR-008**: Los datos almacenados DEBEN permanecer disponibles después de un reinicio normal del producto o del servicio que los gestiona, sin pérdida de registros ya confirmados como guardados.
- **FR-009**: En este entregable, las operaciones de recuperación por identificador y de listado se asumen en **entorno de confianza**: no se exige autenticación ni autorización explícita dentro del producto para acceder a los registros persistidos; la protección frente a accesos no autorizados es responsabilidad del despliegue y del perímetro de red.
- **FR-010**: Este entregable **no** exige plazo máximo de conservación en producto, borrado automático por antigüedad ni operación de eliminación bajo demanda expuesta como requisito funcional; la duración efectiva de los datos y cualquier purga corresponden a **despliegue u operación** (incl. copias de seguridad y gobierno del almacenamiento).
- **FR-011**: Cada finalización de procesamiento que deba persistirse DEBE crear un **nuevo** registro con un identificador **nuevo**; no se exige deduplicación, fusión ni sustitución automática de un registro previo aunque el archivo de origen o el texto de entrada sean iguales o muy similares.

### Key Entities *(include if feature involves data)*

- **Reunión procesada (registro)**: Representa una ejecución completada del procesamiento de una reunión. Incluye identificador único, resultados estructurados en texto (participantes, temas, acciones, minuta, resumen), estado de procesamiento, momento de creación, errores o advertencias opcionales y metadatos opcionales del archivo de origen (nombre, tipo).

### Assumptions

- El volumen inicial permite listar el conjunto completo de registros en una sola operación; si el volumen crece, se podrá añadir paginación en una iteración posterior sin cambiar el significado de los datos almacenados.
- Los campos de resultado se almacenan como texto con convenciones de separación acordadas en el producto (p. ej. listas delimitadas); no se exige un formato de documento enriquecido en esta capacidad.
- La unicidad del identificador es responsabilidad del producto al crear el registro; no se contempla reasignación del mismo identificador a otra reunión.
- Las consultas get/list cumplen el supuesto de entorno de confianza descrito en FR-009; no se define en este alcance un modelo de usuarios ni permisos por rol.
- La política de cuánto tiempo se conservan los datos en el medio de persistencia y cómo se purgan copias externas queda fuera del alcance funcional de esta historia; se asume alineación con prácticas del entorno que despliega el producto.
- No se asume un registro único “por archivo” ni “por reunión lógica” salvo que otra historia lo defina; múltiples ejecuciones implican múltiples filas o documentos persistidos (véase FR-011).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tras guardar un registro y reiniciar el producto, el 100% de las pruebas de verificación muestreadas confirman que la consulta por identificador devuelve los mismos datos que antes del reinicio.
- **SC-002**: Para un conjunto de al menos cinco reuniones guardadas con fechas de creación distintas, el listado las incluye todas y el orden coincide con el criterio “más reciente primero” en el 100% de las comprobaciones.
- **SC-003**: Cada finalización de procesamiento que deba persistirse produce un registro recuperable en menos de 5 segundos desde la confirmación de guardado en condiciones de uso típico (medido desde la perspectiva de quien valida el flujo, no de componentes internos).
- **SC-004**: En pruebas con identificadores inexistentes, el 100% de las solicitudes producen un resultado claramente distinguible de un acierto y sin datos de otra reunión.
