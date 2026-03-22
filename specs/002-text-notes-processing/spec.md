# Feature Specification: Procesar notas en texto

**Feature Branch**: `002-text-notes-processing`  
**Created**: 2025-03-21  
**Status**: Draft  
**Input**: US-002 — Subir archivo TXT o Markdown con notas de reunión para obtener documentación estructurada sin transcripción

## Assumptions

- El flujo base de procesamiento (workflow de extracción y generación de las 5 salidas) ya existe (US-000/001-hello-world-e2e).
- La API y la UI base están operativas; esta feature extiende la capacidad de entrada para aceptar archivos además de texto directo.
- El límite de tamaño es por número de caracteres (50.000); se valida tras leer el contenido del archivo, alineado con el flujo de texto existente.
- La UI presenta en la misma pantalla el área de texto y el selector/área de arrastrar archivo; el usuario elige uno u otro. Mientras una opción tiene contenido, la otra permanece bloqueada; el usuario debe limpiar manualmente antes de cambiar de modo.

## Clarifications

### Session 2025-03-21

- Q: ¿Cómo expone la UI las dos formas de entrada (texto directo vs archivo)? → A: Misma pantalla con área de texto Y selector/área de arrastrar archivo; el usuario elige uno u otro
- Q: ¿Qué indicadores de progreso o estado mostrar durante subida y procesamiento de archivos? → A: Barra de progreso de subida + indicador "Procesando..." durante el análisis
- Q: ¿Cómo se define y valida el límite de tamaño (caracteres vs bytes)? → A: Límite por número de caracteres (ej. 50.000); validar tras leer el contenido
- Q: ¿Qué ocurre cuando hay contenido en texto y el usuario sube archivo (o viceversa)? → A: Bloquear la otra opción mientras una tiene contenido; el usuario debe limpiar manualmente antes de cambiar
- Q: ¿Qué formatos quedan explícitamente fuera de alcance? → A: Solo TXT y MD soportados; PDF, DOCX, ODT y demás formatos binarios quedan explícitamente fuera de alcance

## Out of Scope

- PDF, DOCX, ODT y demás formatos binarios: no soportados en esta feature; rechazar con mensaje indicando formatos soportados (.txt, .md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Subir archivo TXT con notas de reunión (Priority: P1)

Como Marina o Pablo, quiero subir un archivo de texto plano (.txt) con notas tomadas durante o después de una reunión, para obtener documentación estructurada (participantes, temas, acciones, minuta, resumen) sin necesidad de transcripción.

**Why this priority**: Es la ruta de entrada más simple y permite demos rápidas sin depender de servicios de transcripción de voz. Cubre el caso de uso más común para notas escritas.

**Independent Test**: Se puede probar subiendo un archivo .txt con contenido de reunión y verificando que el sistema devuelve las 5 salidas estructuradas sin ejecutar transcripción.

**Acceptance Scenarios**:

1. **Given** tengo un archivo .txt con notas de reunión, **When** subo el archivo al sistema, **Then** el sistema lee el contenido directamente sin transcripción
2. **Given** el archivo fue procesado, **When** examino la respuesta, **Then** incluye participantes, temas, acciones, minuta y resumen estructurados
3. **Given** tengo un archivo .txt válido, **When** lo subo, **Then** el sistema no ejecuta ningún paso de transcripción (STT)
4. **Given** estoy subiendo un archivo, **When** el archivo se transfiere, **Then** veo una barra de progreso; **And** durante el análisis veo indicador "Procesando..."

---

### User Story 2 - Subir archivo Markdown con notas (Priority: P2)

Como Marina o Pablo, quiero subir un archivo Markdown (.md) con notas de reunión en formato estructurado (encabezados, listas, etc.), para obtener la misma documentación estructurada que con TXT, aprovechando el formato existente.

**Why this priority**: Muchos usuarios toman notas en editores que usan Markdown; es un formato común en contextos técnicos (Pablo) y en herramientas de notas modernas.

**Independent Test**: Se puede probar subiendo un archivo .md con contenido formateado y verificando que el sistema procesa correctamente y genera las 5 salidas estructuradas.

**Acceptance Scenarios**:

1. **Given** tengo un archivo .md con notas en formato Markdown, **When** subo el archivo al sistema, **Then** el sistema procesa el contenido correctamente
2. **Given** el archivo fue procesado, **When** examino la respuesta, **Then** genera las 5 salidas estructuradas (participantes, temas, acciones, minuta, resumen)

---

### User Story 3 - Preservar encoding y caracteres especiales (Priority: P3)

Como usuario con contenido en español u otros idiomas, quiero que el sistema respete correctamente el encoding del archivo (UTF-8 por defecto), para que caracteres especiales (ñ, á, é, ü, etc.) se interpreten correctamente y no se corrompan.

**Why this priority**: Garantiza usabilidad en contextos multilingües y evita errores molestos con acentos y caracteres no ASCII.

**Independent Test**: Se puede probar subiendo un archivo con caracteres especiales y verificando que la salida los conserva correctamente.

**Acceptance Scenarios**:

1. **Given** tengo un archivo con caracteres especiales (ñ, á, é, etc.) en UTF-8, **When** subo el archivo, **Then** el contenido se interpreta correctamente en toda la cadena de procesamiento
2. **Given** el archivo tiene encoding distinto a UTF-8, **When** el sistema lo procesa, **Then** intenta interpretarlo correctamente (fallback a latin-1 u otros encodings según corresponda) o informa claramente si no puede leer el archivo

---

### Edge Cases

- ¿Qué ocurre cuando el archivo subido no es TXT ni Markdown (p. ej. PDF, DOCX, ODT)? El sistema rechaza el archivo con un mensaje claro indicando que solo se admiten .txt y .md; formatos binarios quedan explícitamente fuera de alcance.
- ¿Qué ocurre cuando el archivo está vacío o solo contiene espacios? El sistema rechaza con un mensaje de validación apropiado.
- ¿Qué ocurre cuando el archivo supera el límite de caracteres (50.000)? El sistema lee el contenido, valida la longitud y rechaza con 400 y mensaje claro indicando el límite.
- ¿Qué ocurre cuando el MIME type no coincide con la extensión? El sistema valida extensión y/o MIME antes de procesar; rechaza si no es válido.
- ¿Qué ocurre si el usuario tiene texto y luego intenta subir archivo (o viceversa)? La opción sin usar permanece bloqueada; el usuario debe limpiar el contenido actual manualmente antes de cambiar de modo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE aceptar archivos con extensión .txt y .md (text/plain y text/markdown)
- **FR-002**: El sistema DEBE leer el contenido del archivo directamente y pasarlo al workflow de extracción sin ejecutar transcripción (STT)
- **FR-003**: El sistema DEBE generar las 5 salidas estructuradas: participantes, temas, acciones, minuta y resumen
- **FR-004**: El sistema DEBE respetar el encoding del archivo; por defecto UTF-8, con fallback a latin-1 u otro encoding estándar si la lectura con UTF-8 falla
- **FR-005**: El sistema DEBE validar la extensión y, cuando aplique, el MIME type antes de procesar; rechazar con mensaje claro si no es TXT o Markdown
- **FR-006**: El sistema DEBE rechazar archivos vacíos o que solo contengan espacios, con mensaje de validación apropiado
- **FR-007**: El sistema DEBE validar que el contenido leído no exceda 50.000 caracteres; si se excede, rechazar con 400 y mensaje claro indicando el límite
- **FR-008**: El sistema DEBE detectar cuando la entrada es texto desde archivo y procesar el contenido directamente al workflow sin transcripción
- **FR-009**: La UI DEBE mostrar barra de progreso durante la subida del archivo e indicador "Procesando..." durante el análisis; ambos estados visibles para el usuario
- **FR-010**: La UI DEBE bloquear el área de texto cuando hay archivo seleccionado, y bloquear el selector de archivo cuando hay texto en el área; el usuario DEBE limpiar manualmente el contenido actual antes de cambiar de modo

### Key Entities

- **Archivo de notas**: Contenido textual (TXT o Markdown) con notas de reunión; atributos: formato (.txt/.md), encoding (UTF-8 por defecto), contenido
- **Documentación estructurada**: Salida del workflow con 5 componentes: participantes, temas, acciones, minuta, resumen
- **Usuario (Marina/Pablo)**: Personas que suben notas escritas; Marina como asistente, Pablo como desarrollador procesando reuniones técnicas

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden subir un archivo TXT o MD y recibir documentación estructurada en menos de 30 segundos para archivos típicos (hasta 5.000 caracteres)
- **SC-002**: El 100% de los archivos válidos (TXT/MD, encoding correcto, tamaño dentro del límite) se procesan correctamente sin errores de encoding
- **SC-003**: El sistema no ejecuta transcripción en ningún caso cuando la entrada es un archivo de texto; el flujo es exclusivamente lectura → extracción → generación
- **SC-004**: Los usuarios reciben mensajes claros cuando el archivo es rechazado (formato no soportado, vacío, excede límite), permitiendo corregir y reintentar
