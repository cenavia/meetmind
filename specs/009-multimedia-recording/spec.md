# Feature Specification: Procesar grabación multimedia

**Feature Branch**: `009-multimedia-recording`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: US-001 — Subir grabación de reunión (audio o video) para obtener documentación estructurada sin transcribir manualmente

## Clarifications

### Session 2026-03-22

- Q: ¿Cuál debe ser el límite máximo de tamaño de archivo por defecto para grabaciones multimedia? → A: 500 MB (alineado con 008-web-file-upload; soporta reuniones largas o video de calidad).
- Q: ¿Cuál debe ser el timeout por defecto de procesamiento antes de mostrar mensaje de timeout? → A: 15 minutos (margen para transcripciones largas, p. ej. 30 min de audio).
- Q: ¿En qué idioma deben mostrarse los mensajes de error, feedback y timeout? → A: Español (consistente con 008 y MeetMind).
- Q: Cuando el archivo tiene extensión soportada pero el codec no es reconocido, ¿cómo debe comportarse el sistema? → A: Rechazar con mensaje amigable indicando que el formato no es compatible.
- Q: ¿El procesamiento debe ser síncrono o asíncrono? → A: Híbrido — síncrono hasta el timeout (15 min); si tarda más, pasa a asíncrono (job en background, usuario consulta resultado más tarde).

## Assumptions

- Existe un flujo de procesamiento (workflow) que, dado texto de reunión, extrae participantes, temas, acciones, minuta y resumen ejecutivo.
- Marina (asistente) y Pablo (desarrollador) son usuarios objetivo: Marina documenta reuniones grabadas sin escribir manualmente; Pablo procesa stand-ups y retrospectivas grabadas.
- El sistema dispone o dispondrá de capacidades de transcripción de voz a texto (Speech-to-Text).
- Todos los mensajes (feedback, errores, timeout) se presentan en español, alineado con 008-web-file-upload.
- Para archivos de video, el sistema puede obtener la pista de audio para transcribir.

## Out of Scope

- La interfaz de usuario específica para subir archivos (cubierta por US-008 / 008-web-file-upload).
- Autenticación o control de acceso.
- Persistencia o almacenamiento de grabaciones después del procesamiento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir archivo de audio y obtener documentación (Priority: P1)

Como Marina o Pablo, quiero subir un archivo de audio de una reunión grabada (MP3, WAV, M4A u otro formato soportado) y recibir automáticamente la documentación estructurada (participantes, temas, acciones, minuta, resumen ejecutivo) sin transcribir manualmente.

**Why this priority**: Es el flujo principal; permite documentar reuniones de audio de forma automática.

**Independent Test**: Subir archivo MP3 válido, verificar que se transcribe automáticamente, que se ejecuta el workflow estándar y que se devuelven participantes, temas, acciones, minuta y resumen. Verificar que hay feedback durante el procesamiento.

**Acceptance Scenarios**:

1. **Given** tengo un archivo MP3 con una reunión grabada, **When** lo subo al sistema, **Then** el sistema transcribe el audio automáticamente
2. **Given** la transcripción se completa, **When** el workflow finaliza, **Then** recibo participantes, temas, acciones, minuta y resumen ejecutivo
3. **Given** subo un archivo de audio, **When** se está procesando, **Then** recibo feedback durante el procesamiento (indicador de progreso o mensaje)
4. **Given** el archivo es MP3, WAV o M4A, **When** lo subo, **Then** el sistema lo acepta y procesa correctamente

---

### User Story 2 - Subir archivo de video y obtener documentación (Priority: P1)

Como Marina o Pablo, quiero subir un archivo de video de una reunión (MP4, MOV, WEBM, MKV) y recibir la misma documentación estructurada que con audio, extrayendo y transcribiendo el audio del video automáticamente.

**Why this priority**: Muchas reuniones se graban en video; el valor es equivalente al flujo de audio.

**Independent Test**: Subir archivo MP4 válido, verificar que se extrae el audio, se transcribe y se ejecuta el workflow estándar con los resultados esperados.

**Acceptance Scenarios**:

1. **Given** tengo un archivo MP4 con una reunión grabada, **When** lo subo al sistema, **Then** el sistema extrae el audio y lo transcribe
2. **Given** la transcripción del video se completa, **When** el workflow finaliza, **Then** recibo participantes, temas, acciones, minuta y resumen ejecutivo
3. **Given** el archivo es MP4, MOV, WEBM o MKV, **When** lo subo, **Then** el sistema lo acepta y procesa correctamente

---

### User Story 3 - Rechazo de formatos no soportados (Priority: P2)

Como Marina o Pablo, quiero que cuando intente subir un archivo con formato no soportado (ej. .avi, .exe), reciba un mensaje de error claro que indique los formatos permitidos.

**Why this priority**: Evita frustración y reduce soporte; mejora la experiencia.

**Independent Test**: Intentar subir archivo .avi u otro no soportado y verificar que se muestra mensaje claro con los formatos permitidos.

**Acceptance Scenarios**:

1. **Given** tengo un archivo con extensión no soportada (ej. .avi), **When** intento subirlo, **Then** recibo un mensaje de error claro
2. **Given** el mensaje de error, **When** lo leo, **Then** indica los formatos soportados (MP4, MOV, MP3, WAV, M4A, WEBM, MKV)

---

### Edge Cases

- ¿Qué pasa cuando el archivo supera el límite de tamaño (500 MB por defecto)? El sistema debe rechazarlo con un mensaje claro indicando el límite.
- ¿Qué pasa cuando la transcripción tarda más del timeout (15 min por defecto)? El procesamiento pasa a asíncrono: el usuario recibe identificación del job y puede consultar el resultado más tarde; mensaje amigable en español.
- ¿Qué pasa cuando el archivo tiene formato válido pero el contenido está corrupto o no es reconocible? El sistema debe devolver un error claro sin exponer detalles técnicos internos.
- ¿Qué pasa cuando el archivo de video no tiene pista de audio? El sistema debe indicar un error claro.
- ¿Qué pasa con codecs no soportados dentro de contenedores válidos? El sistema rechaza con mensaje amigable indicando que el formato no es compatible, sin exponer detalles técnicos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST aceptar archivos de audio en formatos MP3, WAV, M4A y transcribirlos automáticamente a texto.
- **FR-002**: El sistema MUST aceptar archivos de video en formatos MP4, MOV, WEBM, MKV, extraer la pista de audio y transcribirla automáticamente a texto.
- **FR-003**: El sistema MUST ejecutar el workflow estándar (extracción de participantes, temas, acciones, minuta, resumen ejecutivo) sobre el texto obtenido de la transcripción.
- **FR-004**: El sistema MUST proporcionar feedback al usuario durante el procesamiento (indeterminado o progreso) dado que la transcripción puede tardar varios segundos o minutos.
- **FR-005**: El sistema MUST rechazar archivos con formatos no soportados y devolver un mensaje de error claro que indique los formatos permitidos.
- **FR-006**: El sistema MUST aplicar un límite configurable de tamaño de archivo (500 MB por defecto) y rechazar archivos que lo superen con mensaje claro.
- **FR-007**: El sistema MUST manejar transcripciones largas con timeout configurable (15 minutos por defecto). Hasta el timeout, el procesamiento es síncrono (usuario espera). Si se supera, pasa a asíncrono: el usuario recibe identificación del job y puede consultar el resultado más tarde; el sistema comunica mensaje amigable en español.
- **FR-008**: El sistema MUST soportar los codecs de audio y video más comunes dentro de los contenedores indicados. Si el codec no es reconocido o no se puede procesar, debe rechazar con mensaje amigable indicando que el formato no es compatible.
- **FR-009**: El sistema MUST comunicar errores (archivo corrupto, transcripción fallida, timeout) con mensajes amigables en español, sin exponer detalles técnicos crudos al usuario.
- **FR-010**: Cuando el procesamiento pasa a asíncrono (por superar el timeout), el sistema MUST proporcionar al usuario una identificación del job y MUST permitir consultar el resultado una vez completado.

### Key Entities

- **Archivo multimedia**: Grabación de reunión en formato de audio (MP3, WAV, M4A) o video (MP4, MOV, WEBM, MKV), enviado para transcribir y procesar.
- **Transcripción**: Texto generado a partir del audio mediante reconocimiento de voz.
- **Resultados de procesamiento**: Conjunto estructurado que incluye participantes, temas, acciones, minuta y resumen ejecutivo, obtenido al aplicar el workflow sobre la transcripción.
- **Estado de procesamiento**: Indica si la transcripción y el workflow están en curso, completados o fallidos; usado para dar feedback al usuario.
- **Job asíncrono**: Identificación de un procesamiento que superó el timeout; permite al usuario consultar el resultado más tarde.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Marina o Pablo pueden subir una grabación de reunión (audio o video) y recibir documentación estructurada completa en un tiempo aceptable según duración del archivo (feedback visible durante la espera).
- **SC-002**: El 100% de los intentos con formato no soportado reciben un mensaje de error claro que indica los formatos permitidos (MP4, MOV, MP3, WAV, M4A, WEBM, MKV).
- **SC-003**: El 100% de los errores (archivo corrupto, transcripción fallida, timeout, archivo demasiado grande) se comunican con mensajes amigables, sin exponer detalles técnicos internos.
- **SC-004**: Los archivos de audio y video soportados se procesan correctamente hasta generar participantes, temas, acciones, minuta y resumen ejecutivo en condiciones de uso normal.
- **SC-005**: El sistema maneja reuniones largas: síncrono hasta 15 min; si se supera, pasa a asíncrono y el usuario puede consultar el resultado más tarde con identificación del job.
