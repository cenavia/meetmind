# Feature Specification: Procesar y consultar reuniones vía servicio HTTP

**Feature Branch**: `012-meetings-rest-api`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "US-010: Procesar reuniones vía API REST — integración y automatización (endpoints de procesamiento, historial, detalle, salud del servicio y documentación de interfaz)."

## Clarifications

### Session 2026-03-22

- Q: ¿Tras un procesamiento exitoso por HTTP (texto o archivo), debe crearse siempre un registro persistido cuando exista capacidad de almacenamiento? → A: Sí (opción A): al completar con éxito, debe crearse el mismo tipo de registro que en el flujo que ya persiste; listado y detalle deben reflejar esas ejecuciones.
- Q: ¿El procesamiento por HTTP debe ser síncrono (resultado en la misma respuesta) o asíncrono con sondeo? → A: Síncrono (opción A): el cliente espera hasta el fin del procesamiento en la misma solicitud; los límites de tiempo los fija despliegue y documentación; no se exige contrato de trabajo diferido + consulta posterior en este entregable.
- Q: ¿Un solo endpoint de salud o separar liveness y readiness? → A: Dos comprobaciones documentadas (opción C): una ligera (liveness) y otra de preparación (readiness) con propósito explícito en la documentación.
- Q: Si el almacenamiento persistido falla al atender listado o detalle, ¿listado vacío / “no encontrado” o error explícito? → A: Error del servidor inequívoco (p. ej. servicio no disponible); no simular ausencia de datos con listado vacío ni “no encontrado” cuando la causa es la indisponibilidad del almacenamiento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Procesar una reunión enviando texto (Priority: P1)

**Pablo** (desarrollador) o un **integrador de sistemas** envía el contenido textual de una reunión en una solicitud estructurada y recibe el resultado del procesamiento (participantes, temas, acciones, minuta, resumen) en la misma conversación con el servicio, sin usar interfaz gráfica.

**Why this priority**: Es el camino más simple para automatizar pipelines y pruebas; desbloquea integración sin manejo de archivos.

**Independent Test**: Con el servicio en ejecución, una solicitud válida con cuerpo de texto devuelve un resultado completo y coherente con las reglas de negocio del procesamiento de reuniones.

**Acceptance Scenarios**:

1. **Given** que el servicio está disponible, **When** se envía una solicitud de procesamiento con un cuerpo de texto no vacío que describe una reunión, **Then** la respuesta indica éxito y el cuerpo incluye participantes, temas, acciones, minuta y resumen (o equivalentes acordados en el producto).
2. **Given** que el servicio está disponible, **When** se envía una solicitud de procesamiento con texto vacío o inválido según las reglas de validación, **Then** la respuesta rechaza la solicitud de forma inequívoca y el cuerpo describe el problema de validación sin exponer detalles internos sensibles del sistema.

---

### User Story 2 - Procesar una reunión enviando un archivo (Priority: P1)

El integrador adjunta un archivo (p. ej. texto o multimedia admitido por el producto) y recibe el mismo tipo de resultado estructurado que en el flujo por texto.

**Why this priority**: Muchos orígenes reales llegan como archivos; paridad con el flujo textual mantiene el valor de automatización.

**Independent Test**: Con un archivo de tipo y tamaño permitidos, la solicitud con adjunto devuelve resultado procesado; con archivo no permitido o demasiado grande, la respuesta es un rechazo claro.

**Acceptance Scenarios**:

1. **Given** un archivo cuyo tipo y tamaño están dentro de lo permitido por el producto, **When** se envía una solicitud de procesamiento con ese archivo como adjunto, **Then** la respuesta indica éxito y contiene el resultado estructurado esperado.
2. **Given** un archivo con tipo no admitido o un tamaño por encima del límite configurado, **When** se envía la solicitud, **Then** la respuesta rechaza la solicitud y comunica la causa de forma comprensible para quien integra.

---

### User Story 3 - Comprobar disponibilidad: proceso vivo y servicio preparado (Priority: P2)

Quien opera o integra necesita distinguir si el **proceso** del servicio responde (para reinicios y sondas ligeras) y si el servicio está **preparado** para operaciones que dependen de la persistencia y otras dependencias críticas declaradas.

**Why this priority**: Sin separar ambas señales, orquestadores pueden reiniciar instancias sanas o enviar tráfico antes de que el almacenamiento esté accesible.

**Independent Test**: Con el servicio en ejecución y dependencias sanas, la comprobación de liveness y la de readiness son satisfactorias; con una dependencia crítica indisponible (p. ej. persistencia), la documentación permite interpretar readiness no satisfactorio frente a liveness aún satisfactorio cuando aplique.

**Acceptance Scenarios**:

1. **Given** que el proceso del servicio está en ejecución, **When** se solicita la operación HTTP de **liveness** documentada, **Then** la respuesta indica de forma inequívoca que el proceso responde (estado satisfactorio para ese propósito).
2. **Given** que la persistencia configurada y las dependencias críticas declaradas están disponibles, **When** se solicita la operación HTTP de **readiness** documentada, **Then** la respuesta indica que el servicio está preparado para procesar y consultar reuniones según el contrato.
3. **Given** un escenario en que el proceso responde pero la persistencia configurada no es accesible, **When** se consultan liveness y readiness, **Then** el resultado es coherente con lo documentado para “vivo pero no preparado” (p. ej. readiness no satisfactorio sin afirmar preparación completa).

---

### User Story 4 - Ver historial y detalle de reuniones procesadas (Priority: P2)

El integrador obtiene una lista de reuniones ya procesadas y puede solicitar el detalle completo de una de ellas mediante su identificador.

**Why this priority**: Habilita trazabilidad, auditoría básica y construcción de UIs o informes sobre lo ya ejecutado.

**Independent Test**: Tras existir al menos un registro de reunión disponible para consulta, el listado lo incluye y la consulta por identificador devuelve el mismo contenido que el listado anuncia para ese id.

**Acceptance Scenarios**:

1. **Given** que existen reuniones almacenadas consultables, **When** se solicita el listado, **Then** se recibe una colección que las incluye según las reglas de orden y alcance definidas en el producto.
2. **Given** un identificador de reunión existente, **When** se solicita el detalle por ese identificador, **Then** se recibe el registro completo coherente con lo persistido.
3. **Given** un identificador que no corresponde a ninguna reunión almacenada, **When** se solicita el detalle, **Then** el resultado es inequívoco (p. ej. indicación clara de no encontrado) y no se mezclan datos de otras reuniones.
4. **Given** que la persistencia está activa en el despliegue pero el almacenamiento **no es accesible** al atender la solicitud, **When** se solicita el listado o el detalle por identificador, **Then** la respuesta es un **error del servidor** inequívoco (según documentación) y **no** un listado vacío con éxito ni un “no encontrado” que sugiera identificador inexistente cuando la causa es el fallo de almacenamiento.

---

### User Story 5 - Descubrir y entender las operaciones sin leer código (Priority: P3)

Quien integra accede a una descripción interactiva y actualizada de las operaciones del servicio (parámetros, cuerpos de solicitud, respuestas y códigos de resultado esperados) en una ubicación estable del despliegue.

**Why this priority**: Reduce tiempo de integración y errores de contrato entre cliente y servidor.

**Independent Test**: Sin acceso al repositorio, un integrador puede localizar la documentación, identificar al menos las operaciones de procesamiento, liveness, readiness, listado y detalle, y reproducir una solicitud de ejemplo.

**Acceptance Scenarios**:

1. **Given** el servicio desplegado, **When** se abre la ruta de documentación interactiva acordada, **Then** están descritas las operaciones expuestas con suficiente detalle para construir clientes correctos.

---

### Edge Cases

- Texto vacío o solo espacios: rechazo con mensaje de validación claro.
- Archivo ausente o campo de archivo incorrecto en solicitudes multipart: rechazo claro.
- Tipos MIME o extensiones no admitidas: rechazo sin ejecutar procesamiento costoso cuando la validación lo permita de forma temprana.
- Límite de tamaño de archivo superado: rechazo con indicación de límite o política (sin volcar trazas internas).
- Fallo interno durante procesamiento: respuesta de error del servidor distinta de errores de validación del cliente, sin exponer trazas ni secretos.
- Listado cuando no hay registros **y el almacenamiento respondió correctamente**: colección vacía con éxito, claramente distinta de un fallo de almacenamiento (véase FR-014).
- Almacenamiento no accesible al atender listado o detalle (persistencia activa): error del servidor inequívoco; no confundir con “cero reuniones” ni con identificador inexistente (FR-014).
- Concurrencia: múltiples solicitudes simultáneas válidas deben comportarse de forma definida (cada una recibe su propia respuesta; no se exige serialización global salvo que otra historia lo imponga).
- Cliente y servicio en orígenes distintos (p. ej. navegador): la posibilidad de completar solicitudes depende de la política de despliegue; quien despliega configura la política de origen cruzado acorde a su entorno.
- Procesamiento HTTP **exitoso** con persistencia activa en el despliegue: debe quedar un registro consultable por listado y detalle, coherente con la respuesta de la operación de procesamiento. Entradas rechazadas por validación o fallos de servidor sin resultado persistible no crean registro de éxito.
- Procesamientos de larga duración: el cliente mantiene la solicitud abierta hasta respuesta final o hasta que intervenga un límite de tiempo del despliegue o del cliente; **no** se exige en este entregable devolver solo un identificador de trabajo pendiente con resultado vía sondeo posterior.
- **Liveness** satisfactoria con **readiness** no satisfactoria: debe ser un estado posible y **distinguible** (p. ej. almacenamiento no accesible) sin contradecir la documentación de cada comprobación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El producto DEBE exponer una operación HTTP para enviar texto plano estructurado (p. ej. cuerpo JSON con un campo de texto) y obtener el resultado del procesamiento de reunión cuando la entrada es válida.
- **FR-002**: El producto DEBE exponer una operación HTTP para enviar un archivo como parte de una solicitud multiparte y obtener el resultado del procesamiento cuando el archivo es válido según tipo y tamaño permitidos.
- **FR-003**: El producto DEBE exponer una operación HTTP para listar las reuniones procesadas disponibles para consulta, con un orden predecible (por defecto: más recientes primero, alineado con la capacidad de persistencia del producto si existe).
- **FR-004**: El producto DEBE exponer una operación HTTP para obtener el detalle completo de una reunión por su identificador cuando exista; cuando no exista, DEBE responder de forma inequívoca sin filtrar datos ajenos.
- **FR-005**: El producto DEBE exponer **dos** operaciones HTTP de comprobación **distintas** y descritas en la documentación interactiva: (1) **Liveness**: comprobación **ligera** de que el proceso del servicio responde (p. ej. para sondas de reinicio). (2) **Readiness**: comprobación de que el servicio está **preparado** para operaciones que dependen del almacenamiento persistido configurado y de **otras dependencias críticas** enumeradas explícitamente en la documentación del producto. Debe poder distinguirse con claridad el caso “proceso vivo pero no preparado” frente a “preparado”, mediante códigos de resultado HTTP y/o cuerpos de respuesta acordes con lo documentado.
- **FR-006**: Las rutas y versionado de las operaciones anteriores DEBEN ser estables y documentadas para integradores (p. ej. prefijo de versión en la ruta); las rutas exactas forman parte del contrato de producto descrito en la documentación interactiva.
- **FR-007**: Para entradas inválidas (validación), el producto DEBE usar códigos de resultado HTTP apropiados para “error del cliente” (p. ej. solicitud incorrecta o no procesable) y un cuerpo que explique el fallo de validación de forma segura.
- **FR-008**: Para fallos internos no atribuibles a errores de validación del cliente, el producto DEBE usar códigos de resultado HTTP apropiados para “error del servidor” y mensajes genéricos que no expongan trazas ni datos sensibles.
- **FR-009**: El producto DEBE publicar documentación interactiva de las operaciones expuestas en una ruta estable del despliegue (p. ej. ruta `/docs` o equivalente documentada), actualizada con el contrato vigente.
- **FR-010**: Las operaciones de listado y detalle asumen el mismo supuesto de **entorno de confianza** que la consulta a registros persistidos: no se exige autenticación ni autorización explícita dentro del producto en este entregable; la protección perimetral es responsabilidad de quien despliega.
- **FR-011**: Los límites de tamaño de archivo y las reglas de tipos admitidos DEBEN ser aplicados de forma consistente y, cuando sea posible, configurables por despliegue dentro de límites razonables definidos por el producto.
- **FR-012**: Cuando en el despliegue esté activa la capacidad de persistencia de reuniones procesadas, tras un procesamiento **exitoso** iniciado por la operación HTTP de envío de texto o por la de envío de archivo, el producto **DEBE** crear un registro persistido con el mismo criterio que al finalizar el flujo interno que ya guarda resultados (incluido un identificador estable recuperable vía listado y detalle). No se exige crear registro para solicitudes fallidas por validación del cliente ni para errores de servidor sin resultado persistible acordado con las reglas de la capacidad de persistencia.
- **FR-013**: Las operaciones HTTP de procesamiento por texto y por archivo DEBEN ser **síncronas** respecto al trabajo de negocio: la respuesta **exitosa** solo se emite cuando el procesamiento ha terminado y el cuerpo incluye el **resultado estructurado completo** (o la respuesta de error acotada correspondiente). Queda **fuera de alcance** de este entregable un contrato donde la respuesta inicial indique únicamente trabajo aceptado o pendiente y el resultado deba obtenerse mediante otra operación de consulta o sondeo.
- **FR-014**: Cuando la persistencia esté **activa** en el despliegue y una operación de **listado** o **detalle** requiera leer el almacenamiento configurado, si ese almacenamiento **falla o es inaccesible** en el momento de atender la solicitud, el producto DEBE responder con un **error del servidor** inequívoco (código de resultado HTTP y cuerpo documentados para indisponibilidad o fallo de almacenamiento, sin exponer trazas ni secretos). **NO** DEBE devolver un listado vacío con éxito ni un resultado interpretable como “no hay reuniones”, ni en detalle un “no encontrado” equivalente a identificador inexistente, cuando la causa real es la imposibilidad de leer el almacenamiento.

### Key Entities *(include if feature involves data)*

- **Resultado de procesamiento de reunión**: Conjunto estructurado devuelto tras un procesamiento exitoso (participantes, temas, acciones, minuta, resumen y campos afines definidos por el producto).
- **Registro de reunión (historial)**: Representación de una ejecución ya procesada y almacenada para consulta, con identificador estable y metadatos necesarios para listado y detalle (alineado con la capacidad de persistencia cuando esté activa).

### Assumptions

- Existe un flujo de negocio de procesamiento de reuniones que produce el resultado estructurado; esta historia define cómo se expone y consume vía HTTP, no redefine el algoritmo interno del procesamiento salvo requisitos de validación de entrada.
- Las operaciones de listado y detalle operan sobre los registros persistidos de reuniones procesadas. Si en un despliegue la persistencia no está activa, listado y detalle reflejan esa limitación (p. ej. conjunto vacío o comportamiento documentado para ese modo), sin contradecir FR-012 cuando la persistencia sí esté activa.
- El volumen inicial permite devolver el listado completo en una sola respuesta; si el volumen crece, se podrá añadir paginación en una iteración posterior sin cambiar el significado de los datos.
- La política de orígenes cruzados para clientes web en dominios distintos la define quien despliega; el producto debe permitir configurarla cuando el entorno lo requiera.
- No se introduce en este alcance un modelo de usuarios, API keys ni permisos por rol; la seguridad de acceso al servicio HTTP es responsabilidad del perímetro de red y del despliegue.
- Los tiempos máximos aceptables de una solicitud de procesamiento síncrono los acuerdan despliegue, cliente HTTP y documentación del producto; superarlos puede producir cierre de conexión o error sin resultado completo, sin obligar a introducir procesamiento asíncrono en esta historia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un ensayo controlado, el 100% de las solicitudes de procesamiento por texto válido completan con éxito y devuelven los cinco bloques de resultado acordados (participantes, temas, acciones, minuta, resumen) en la respuesta.
- **SC-002**: En un ensayo con archivos válidos de cada tipo principal admitido por el producto, al menos el 95% de las solicitudes multipart válidas completan con éxito sin intervención manual; las no válidas reciben rechazo con mensaje comprensible en el 100% de los casos de prueba definidos.
- **SC-003**: En pruebas de validación (texto vacío, archivo no permitido, tamaño excedido), el 100% de los casos producen un código de resultado de “error del cliente” y un cuerpo que identifica el tipo de fallo sin exponer trazas internas.
- **SC-004**: Un integrador sin acceso al código fuente puede, en menos de 15 minutos desde la URL base del servicio, localizar la documentación interactiva, identificar las operaciones de procesamiento (texto y archivo), **liveness**, **readiness**, listado y detalle, y ejecutar con éxito al menos una solicitud de ejemplo de cada categoría principal (texto, liveness) usando solo la documentación y una herramienta estándar de cliente HTTP.
- **SC-005**: La comprobación de **liveness** responde con estado satisfactorio en menos de 2 segundos en condiciones típicas de despliegue local o de prueba, en el 95% de las mediciones tomadas durante una ventana de prueba de 10 minutos.
- **SC-009**: En un escenario de prueba donde la persistencia configurada no es accesible pero el proceso del servicio sigue respondiendo, el 100% de las repeticiones muestran que la operación de **readiness** **no** es satisfactoria (según lo documentado) mientras la **liveness** puede seguir siendo satisfactoria, sin ambigüedad entre ambas.
- **SC-006**: Para identificadores inexistentes en detalle de reunión, el 100% de las solicitudes de prueba producen un resultado claramente distinguible de un acierto y sin datos de otra reunión.
- **SC-007**: Con persistencia activa, tras una solicitud HTTP de procesamiento por texto o por archivo que finalice con **éxito**, el 100% de los casos de prueba muestreados incluyen el nuevo registro en el listado y el detalle por identificador es coherente con los datos devueltos en la respuesta de procesamiento.
- **SC-008**: En pruebas de procesamiento síncrono por texto y por archivo (entradas válidas de complejidad típica), el 100% de las respuestas **exitosas** incluyen en **una sola** respuesta HTTP el resultado estructurado final, sin requerir una segunda operación de sondeo para obtener ese resultado.
- **SC-010**: En un escenario de prueba donde la persistencia está activa y se simula fallo de almacenamiento al atender el listado o el detalle, el 100% de las solicitudes producen un resultado clasificable como **error del servidor** inequívoco, **distinguible** tanto de una respuesta **exitosa** con listado vacío legítimo como de un “no encontrado” por identificador inexistente.
