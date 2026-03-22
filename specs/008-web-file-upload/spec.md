# Feature Specification: Subir archivos desde la interfaz web

**Feature Branch**: `008-web-file-upload`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: US-008 — Subir archivos desde la interfaz web para procesar reuniones sin usar la línea de comandos ni la API directamente

## Clarifications

### Session 2026-03-22

- Q: ¿Cuál es la lista exacta de formatos soportados? → A: Multimedia (MP4, MOV, MP3, WAV, M4A), texto (TXT, MD). Ajustable cuando la API lo especifique.
- Q: ¿Cuál es el tamaño máximo de archivo? → A: 500 MB (permitir reuniones largas o vídeo de alta calidad).
- Q: ¿Cuál es el timeout de procesamiento? → A: 10 minutos (margen amplio para procesamiento pesado).
- Q: ¿En qué idioma deben estar la interfaz y los mensajes? → A: Siempre español (consistencia con MeetMind y usuarios objetivo).
- Q: ¿Comportamiento del botón Procesar sin archivo cargado? → A: Deshabilitado hasta que haya archivo seleccionado (evita clics vacíos).

## Assumptions

- Existe un servicio de procesamiento (API) que acepta archivos y devuelve participantes, temas, acciones, minuta y resumen ejecutivo.
- Marina (asistente) y Pablo (desarrollador) son usuarios objetivo: Marina sin conocimientos técnicos, Pablo para demos o procesamiento rápido.
- La interfaz comparte el flujo con otras features del proyecto (botones «Procesar» y «Limpiar» según 007-executive-summary).
- Toda la interfaz (etiquetas, mensajes, feedback, errores) se presenta en español.

## Out of Scope

- Autenticación o control de acceso a la interfaz.
- Procesamiento de archivos sin interfaz web (CLI, API directa).
- Personalización del tema o estilos de la interfaz.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cargar archivo válido y ver resultados (Priority: P1)

Como Marina o Pablo, quiero seleccionar un archivo válido (multimedia o texto), pulsar un botón para procesarlo y ver los resultados estructurados (participantes, temas, acciones, minuta, resumen) en la interfaz, sin usar comandos ni la API directamente.

**Why this priority**: Es el flujo principal; habilita el valor central de procesar reuniones desde la web.

**Independent Test**: Subir archivo TXT o MP3 válido, pulsar procesar, verificar que aparece feedback durante la carga y el procesamiento, y que se muestran los resultados en secciones claras.

**Acceptance Scenarios**:

1. **Given** tengo un archivo TXT o MP3 (u otro formato soportado), **When** lo selecciono y pulso «Procesar», **Then** veo feedback visual durante la carga
2. **Given** el archivo se está procesando, **When** espero, **Then** veo un indicador de procesamiento
3. **Given** el procesamiento termina correctamente, **When** miro la interfaz, **Then** recibo los resultados estructurados (participantes, temas, acciones, minuta, resumen)
4. **Given** los resultados, **When** los reviso, **Then** están organizados en secciones claras (tabs o colapsables)

---

### User Story 2 - Validación de tipos de archivo (Priority: P1)

Como Marina o Pablo, quiero que la interfaz valide los tipos de archivo antes de enviar, y que si selecciono un formato no soportado (ej. .exe, .zip), reciba un mensaje de error claro que indique los formatos soportados.

**Why this priority**: Evita frustración y malentendidos; mejora la experiencia de usuarios no técnicos.

**Independent Test**: Intentar subir archivo .exe o .zip, verificar que no se envía y que se muestra mensaje con formatos soportados.

**Acceptance Scenarios**:

1. **Given** selecciono un archivo .exe, .zip o que supera 500 MB, **When** intento procesarlo, **Then** recibo un mensaje de error claro
2. **Given** el mensaje de error, **When** lo leo, **Then** indica los formatos soportados (multimedia: MP4, MOV, MP3, WAV, M4A; texto: TXT, MD)
3. **Given** archivo no válido, **When** intento procesar, **Then** el sistema no envía el archivo al servicio

---

### User Story 3 - Errores de procesamiento amigables (Priority: P2)

Como Marina o Pablo, quiero que cuando ocurra un error durante el procesamiento (fallo del servicio, timeout, etc.), la interfaz muestre un mensaje amigable y no exponga errores técnicos crudos.

**Why this priority**: Protege la experiencia del usuario y evita confusión ante fallos.

**Independent Test**: Simular error de la API y verificar que el mensaje mostrado es comprensible y no técnico.

**Acceptance Scenarios**:

1. **Given** ocurre un error durante el procesamiento, **When** el servicio retorna error, **Then** la interfaz muestra un mensaje amigable al usuario
2. **Given** un error técnico, **When** se muestra al usuario, **Then** no se exponen detalles técnicos crudos (stack traces, códigos HTTP internos)
3. **Given** un error, **When** el usuario lo ve, **Then** puede entender qué ha pasado y qué hacer (ej. reintentar, verificar archivo)

---

### User Story 4 - Configuración de URL del servicio (Priority: P3)

Como Pablo (desarrollador), quiero poder configurar la URL del servicio de procesamiento (por variable de entorno o campo en la interfaz) para usar la API en diferentes entornos (local, staging, producción).

**Why this priority**: Necesario para demos y despliegues; menos crítico para Marina que usa el valor por defecto.

**Independent Test**: Configurar URL distinta y verificar que la interfaz consume ese endpoint.

**Acceptance Scenarios**:

1. **Given** la interfaz está desplegada, **When** se configura una URL de API (env o input), **Then** la interfaz usa esa URL para enviar archivos
2. **Given** Pablo ejecuta la interfaz en local, **When** configura la URL de su API local, **Then** los archivos se envían a esa API

---

### Edge Cases

- ¿Qué pasa cuando no hay archivo cargado? El botón «Procesar» está deshabilitado hasta que el usuario seleccione un archivo; no se envía petición vacía.
- ¿Qué pasa cuando el archivo supera 500 MB? La interfaz debe rechazarlo antes de enviar y mostrar mensaje amigable indicando el límite.
- ¿Qué pasa cuando el archivo es válido pero tarda más de 10 minutos en procesarse? La interfaz debe mostrar indicador de progreso; si el servicio no responde en 10 minutos, mostrar mensaje amigable indicando timeout y sugerir reintentar.
- ¿Qué pasa cuando la API devuelve resultados parciales (ej. solo participantes, sin minuta)? Mostrar lo disponible; si falta algo crítico, mensaje claro indicando qué no se pudo obtener.
- ¿Qué pasa cuando el usuario sube un archivo con extensión válida pero contenido corrupto o no reconocible? El servicio puede rechazarlo; la interfaz debe mostrar mensaje amigable sin detalles técnicos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La interfaz web MUST ofrecer un componente de carga (upload) que acepte archivos multimedia (MP4, MOV, MP3, WAV, M4A) y texto (TXT, MD). La lista es ajustable cuando el servicio de procesamiento lo especifique.
- **FR-002**: La interfaz MUST mostrar feedback visual durante la carga del archivo (indicador de progreso o similar).
- **FR-003**: La interfaz MUST mostrar feedback visual durante el procesamiento (ej. mensaje «Procesando...» o spinner).
- **FR-004**: La interfaz MUST visualizar los resultados en secciones claras: participantes, temas, acciones, minuta, resumen ejecutivo (tabs o colapsables).
- **FR-005**: La interfaz MUST validar los tipos de archivo y el tamaño antes de enviar; solo permitir formatos soportados (multimedia: MP4, MOV, MP3, WAV, M4A; texto: TXT, MD) y tamaño máximo 500 MB.
- **FR-006**: La interfaz MUST mostrar mensajes de error claros y amigables (en español) cuando el archivo no es válido, supera el límite, el procesamiento falla o hay timeout (10 minutos); no exponer errores técnicos crudos.
- **FR-007**: La interfaz MUST enviar los archivos al servicio de procesamiento y recibir los resultados estructurados.
- **FR-008**: La interfaz MUST permitir configurar la URL del servicio de procesamiento (variable de entorno o input de configuración).
- **FR-009**: La interfaz MUST seguir un layout claro: zona de upload → botón procesar → área de resultados. Todas las etiquetas y mensajes en español.
- **FR-010**: La interfaz MUST desactivar el botón «Procesar» tras hacer clic (alineado con 007-executive-summary) hasta que el usuario use «Limpiar». El botón «Procesar» MUST estar deshabilitado cuando no hay archivo seleccionado.

### Key Entities

- **Archivo subido**: Contenido multimedia (MP4, MOV, MP3, WAV, M4A) o textual (TXT, MD), hasta 500 MB, que el usuario envía para procesar.
- **Resultados de procesamiento**: Conjunto estructurado que incluye participantes, temas, acciones, minuta, resumen ejecutivo.
- **Estado de carga**: Indica si hay archivo seleccionado, si está cargando o si ya está listo para procesar.
- **Estado de procesamiento**: Indica si la solicitud está en curso, completada o fallida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Marina o Pablo pueden procesar una reunión desde la interfaz web en menos de 2 minutos (incluyendo carga, envío y visualización de resultados).
- **SC-002**: El 100% de los intentos con archivo no soportado reciben un mensaje de error claro que indica los formatos permitidos.
- **SC-003**: El 100% de los errores (archivo inválido, timeout de 10 min, fallo del servicio) se muestran con mensajes amigables, sin exponer stack traces ni códigos internos al usuario.
- **SC-004**: Los resultados se presentan en secciones diferenciadas (participantes, temas, acciones, minuta, resumen) de forma que el usuario pueda localizarlos en menos de 10 segundos.
