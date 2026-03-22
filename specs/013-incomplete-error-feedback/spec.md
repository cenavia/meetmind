# Feature Specification: Feedback claro ante información incompleta y errores

**Feature Branch**: `013-incomplete-error-feedback`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "US-011: Recibir feedback ante información incompleta o errores; mensajes claros, estados partial/failed, processing_errors, UI separada, copiar transcripción cuando exista"

## Clarifications

### Session 2026-03-22

- Q: ¿Solo la interfaz gráfica o también las respuestas de la API HTTP deben cumplir la misma política de mensajes legibles y sin trazas? → A: **Interfaz y API alineadas (opción A):** mismos principios de mensajes legibles, estado de negocio y advertencias estructuradas; sin trazas ni excepciones internas en el cuerpo expuesto a clientes genéricos; códigos y significado HTTP según convenciones documentadas del producto.
- Q: ¿Cómo definir “texto muy corto” para disparar advertencias? → A: **Umbral fijo en palabras (opción A):** valor predeterminado de negocio **20 palabras**; el plan técnico documenta el entero final N y la regla de recuento (p. ej. palabras separadas por espacios en el texto de entrada principal). Si se cambia N, debe quedar trazable en documentación de producto.
- Q: ¿Cómo presentar muchas advertencias en la interfaz si la lista es larga? → A: **Opción A — Todas visibles:** el bloque de avisos muestra **todas** las entradas; si el listado es largo, el área permite **desplazamiento** (scroll) para leer cada mensaje completo; no se sustituye la lista por un resumen que oculte el texto individual. La API sigue devolviendo la colección estructurada completa.
- Q: ¿Idioma de mensajes y etiquetas en esta entrega? → A: **Solo español (opción A):** mensajes al usuario, advertencias, etiquetas de estado, validaciones y textos equivalentes en cuerpos HTTP del contrato público orientados a personas están en **español** en el alcance de esta feature.
- Q: ¿Quién puede ver el bloque opcional de detalles técnicos/de despliegue en la interfaz? → A: **Opción A — Cualquier usuaria:** el bloque permanece **colapsado por defecto** y separado del mensaje principal de error; **cualquier usuaria** puede expandirlo si existe contenido opcional que mostrar; no se exige rol administrativo ni modo diagnóstico para verlo en esta entrega (sin incluir secretos ni credenciales en ese contenido).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Entender qué ocurrió sin jerga técnica (Priority: P1)

**Marina** u otra persona usuaria procesa una reunión y el resultado es incompleto, de baja calidad o falla por un problema del servicio (p. ej. transcripción no disponible, tiempo de espera agotado). Recibe una explicación en lenguaje cotidiano, una indicación clara de si el procesamiento fue **completado**, **parcial** o **fallido**, y, cuando aplique, sugerencias concretas (reintentar, probar otro archivo, aportar más texto, comprobar conectividad).

**Why this priority**: Sin esto, los fallos generan desconfianza, soporte informal y abandono; es el núcleo de la promesa de la historia de usuario.

**Independent Test**: Simulando o provocando cada tipo de resultado (éxito pleno, parcial por calidad o datos, fallo por servicio), se verifica que los mensajes visibles no contienen trazas técnicas ni textos de error internos y que el estado se entiende sin conocer el producto por dentro.

**Acceptance Scenarios**:

1. **Given** que el texto no permite identificar participantes con nombre, **When** el sistema termina de procesar, **Then** la sección de participantes está vacía o indica explícitamente que no se identificaron, sin mostrar error técnico.
2. **Given** que el texto de entrada tiene **menos de 20 palabras** (o menos de N palabras si el plan fija otro N documentado), **When** el sistema procesa, **Then** hay al menos una advertencia legible relacionada con la brevedad o calidad, los resultados parciales se muestran si existen y el estado puede ser **parcial**.
3. **Given** que la transcripción desde audio o vídeo falla, **When** la persona consulta el resultado, **Then** el estado es **fallido**, la descripción es comprensible (p. ej. que no se pudo obtener la transcripción) y los avisos no se presentan como si fueran contenido analítico válido.
4. **Given** que una operación de análisis automático supera el tiempo de espera aceptado, **When** ocurre el fallo, **Then** la persona ve un mensaje comprensible y, cuando tenga sentido, se le sugiere reintentar.

---

### User Story 2 - Validar la entrada antes de procesar (Priority: P1)

La persona intenta iniciar el procesamiento sin texto ni archivo válido, o con un archivo no admitido. Recibe un mensaje claro sobre qué falta o qué no es válido **en el mismo flujo** que el botón o acción principal de procesar, no en un canal oculto o solo para administración.

**Why this priority**: Evita ciclos de prueba y error y reduce la sensación de que “la aplicación no hace nada”.

**Independent Test**: Con la interfaz principal, intentar procesar con campo vacío, archivo no permitido o combinación inválida; cada caso muestra mensaje comprensible en contexto de la acción.

**Acceptance Scenarios**:

1. **Given** que no hay texto ni archivo seleccionado, **When** la persona confirma procesar, **Then** ve qué dato falta sin mensaje técnico crudo.
2. **Given** que el archivo no es de un tipo admitido o excede el tamaño permitido, **When** confirma procesar, **Then** la causa se explica de forma comprensible en el flujo de la pantalla de trabajo.

---

### User Story 3 - Separar avisos del análisis y mantener detalles operativos aparte (Priority: P2)

Los avisos y descripciones de fallo aparecen en un **bloque claramente titulado** y visualmente distinto del contenido del análisis (participantes, temas, acciones, minuta, resumen). Los estados **completado**, **parcial** y **fallido** se comunican con **texto explícito** (etiqueta o frase), además de cualquier uso de color. La información dirigida a quien despliega el servicio (modo de transcripción, variables de entorno, etc.) no se mezcla con los mensajes para la usuaria final; si se muestra, va en una sección **colapsada por defecto**.

**Why this priority**: Reduce la carga cognitiva y evita confundir contenido generado con mensajes del sistema.

**Independent Test**: Con resultados que incluyen advertencias y secciones de análisis, un observador puede señalar dos zonas distintas (avisos vs análisis) sin leer el código. Con detalles operativos disponibles, estos no aparecen en el mismo párrafo que el mensaje principal de error para la usuaria.

**Acceptance Scenarios**:

1. **Given** que el procesamiento devolvió advertencias y también fragmentos de análisis, **When** se muestra la pantalla de resultado, **Then** las advertencias están agrupadas en un bloque dedicado separado de las secciones de análisis.
2. **Given** que el resultado tiene estado **parcial** o **fallido**, **When** una persona con visión típica o solo lectura de etiquetas revisa la pantalla, **Then** puede identificar el estado leyendo palabras, no dependiendo solo del color.
3. **Given** que existe información técnica de despliegue opcional para mostrar, **When** la usuaria abre la pantalla, **Then** esa información no compite con el mensaje principal, está en una sección plegable **cerrada inicialmente** y puede expandirla **cualquier usuaria** sin rol especial.

---

### User Story 4 - Copiar la transcripción final cuando exista (Priority: P2)

Si el flujo incluyó transcripción de audio o vídeo y el sistema dispone del texto transcrito para mostrar, la interfaz ofrece una zona claramente etiquetada como transcripción y una **acción explícita** para copiar todo el texto al portapapeles sin depender solo de seleccionar manualmente un bloque muy largo. Si el flujo fue solo texto pegado o documento ya textual, esa zona puede ocultarse o mostrarse vacía según criterio de producto, sin confundirse con el resumen ni con el bloque de avisos.

**Why this priority**: Permite reutilizar el texto en correo, documentos u otras herramientas; es un entregable explícito de la historia de usuario.

**Independent Test**: Tras un procesamiento con transcripción disponible, la persona activa la acción de copiar y pega en un editor verificando el texto completo. Tras flujo sin transcripción, no se exige el mismo control o queda claramente vacío/oculto.

**Acceptance Scenarios**:

1. **Given** que el procesamiento multimedia completó y hay texto de transcripción disponible para la interfaz, **When** la persona usa la acción de copiar asociada a la transcripción, **Then** puede pegar el contenido completo en otro lugar sin seleccionar todo el bloque a mano.
2. **Given** que no hubo paso de transcripción desde audio o vídeo, **When** se muestra el resultado, **Then** la transcripción no se confunde con el resumen ejecutivo ni con el bloque de avisos (oculta, vacía o no aplicable de forma coherente).

---

### User Story 5 - Misma lógica de presentación en historial (Priority: P3)

Cuando exista una vista de **historial de reuniones**, al abrir el detalle de un elemento **parcial** o **fallido** se aplica el mismo patrón que en el flujo principal: bloque de avisos, estado en texto y secciones de resultado vacías o parciales según corresponda.

**Why this priority**: Coherencia entre pantallas evita que la usuaria reaprenda el significado de los estados.

**Independent Test**: Con historial habilitado, abrir un registro en estado parcial o fallido y comparar con el patrón de la vista de procesamiento actual.

**Acceptance Scenarios**:

1. **Given** que el historial está disponible y existe un registro en estado **parcial** o **fallido**, **When** la persona abre el detalle, **Then** ve avisos separados del análisis y el estado identificable por texto, alineado con el flujo principal.

---

### Edge Cases

- Resultados donde solo algunas secciones tienen contenido (p. ej. temas sin acciones): el estado puede ser **parcial** y las secciones vacías no deben parecer “contenido válido omitido por error de pantalla”.
- Antes de la primera acción de la usuaria, la zona de resultado puede mostrar un estado vacío amable; los mensajes de “no enviaste nada” no deben sustituir de forma confusa ese estado cuando aún no ha habido intento de procesar.
- Múltiples advertencias acumuladas durante el procesamiento: **todas** deben ser visibles en el bloque de avisos, con **desplazamiento** en la interfaz si hace falta, sin sobrescribir entradas ni sustituir la lista por un resumen que oculte el texto de cada aviso.
- Si el contrato entre servicio e interfaz aún no expone el texto de transcripción en flujos multimedia, la historia de copiar transcripción queda bloqueada hasta que ese dato esté disponible para la capa de presentación (dependencia explícita con el hilo de trabajo que exponga el campo acordado).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El producto DEBE comunicar el resultado del procesamiento con un estado de negocio explícito: completado, parcial o fallido, comprensible sin conocimiento técnico.
- **FR-002**: El producto DEBE exponer una lista o secuencia estructurada de advertencias y errores no fatales acumulables durante el procesamiento, cuando el motor de análisis las genere.
- **FR-003**: El producto NO DEBE mostrar a la usuaria final trazas de error internas, excepciones sin procesar ni mensajes dirigidos exclusivamente a desarrolladores en el recorrido principal de uso.
- **FR-013**: Las respuestas del contrato HTTP público del producto para procesamiento y detalle de reunión DEBEN ser coherentes con la política anterior: cuerpos con estado de negocio comprensible, advertencias en forma estructurada cuando aplique y **sin** trazas de pila ni textos de excepción interna en lo entregado a clientes genéricos; los códigos HTTP y su interpretación se documentan de forma alineada con estos mensajes.
- **FR-004**: La interfaz principal DEBE mostrar advertencias y descripciones de fallo en un bloque visual o semántico dedicado, separado del contenido del análisis (participantes, temas, acciones, minuta, resumen). **Todas** las entradas de la colección estructurada de advertencias DEBEN poder leerse en ese bloque (p. ej. mediante desplazamiento vertical si el listado es largo); no se DEBE sustituir la lista por un único resumen que oculte el texto individual de cada aviso.
- **FR-005**: Los estados completado, parcial y fallido DEBEN ser identificables mediante texto (etiqueta o frase), no solo mediante color.
- **FR-006**: Las validaciones de entrada vacía, archivo no válido o archivo fuera de política DEBEN producir mensajes comprensibles mostrados en el flujo inmediato de la acción de procesar.
- **FR-007**: Cualquier detalle operativo o de despliegue opcional mostrado en la interfaz NO DEBE mezclarse en el mismo bloque que el mensaje principal de error o advertencias de tarea; si se ofrece, DEBE estar en una **sección colapsable cerrada por defecto**, expandible por **cualquier usuaria**, sin competir visualmente con el mensaje principal hasta que se expanda. Ese contenido **no** DEBE incluir secretos, contraseñas ni claves de API; el plan documenta qué metadatos seguros pueden mostrarse.
- **FR-008**: Cuando el flujo haya producido transcripción completa desde audio o vídeo y el texto esté disponible para la interfaz, esta DEBE ofrecer una acción explícita de copiar todo el texto de la transcripción y una etiqueta clara que la distinga de avisos y del resumen.
- **FR-009**: Los mensajes de error o advertencia DEBEN incluir, cuando sea razonable, una acción sugerida siguiente (reintentar, cambiar archivo, aportar más texto, comprobar conexión).
- **FR-010**: La presentación visual DEBE mantener jerarquía clara entre zona de entrada, zona de resultado y navegación global (p. ej. acceso a historial cuando exista), de modo que en escritorio la lectura siga un orden lógico; en pantallas estrechas el orden apilado DEBE seguir siendo comprensible.
- **FR-011**: La apariencia (colores de acento, fondos, bordes de paneles de avisos y estados) DEBE ser coherente entre controles estándar y paneles personalizados de estado o carga, incluyendo soporte razonable de tema claro y oscuro sin perder contraste en avisos.
- **FR-012**: Cuando exista historial de reuniones, el detalle de ítems parciales o fallidos DEBE reutilizar el mismo patrón de avisos separados, estado textual y secciones de resultado que el flujo principal.
- **FR-014**: Para entradas procesadas como **texto de reunión** (no como sustituto de reglas específicas de transcripción multimedia salvo que el plan indique lo contrario), si el contenido tiene **menos de 20 palabras**, el sistema DEBE añadir al menos una advertencia legible a la colección estructurada de advertencias. El plan técnico documenta el recuento exacto (regla por defecto: palabras delimitadas por espacios en el texto enviado) y puede sustituir 20 por otro entero N ≥ 1 con justificación breve en documentación de producto. Puede aplicarse estado **parcial** cuando existan resultados analíticos aún útiles.
- **FR-015**: En el alcance de esta feature, los textos orientados a personas (interfaz y fragmentos de mensaje en respuestas HTTP del contrato público) DEBEN redactarse en **español**; no se exige soporte multiidioma en este entregable.

### Key Entities

- **Resultado de procesamiento**: Representa el desenlace de una ejecución: estado global (completado, parcial, fallido), descripción legible del fallo si aplica, colección de advertencias, secciones de análisis (cada una puede estar vacía o incompleta) y, opcionalmente, texto de transcripción final cuando el flujo lo haya generado.
- **Advertencia de procesamiento**: Mensaje corto en lenguaje natural, puede acumularse con otras; se distingue del contenido analítico generado (minuta, temas, etc.).

### Assumptions

- El motor de análisis y el servicio de aplicación ya pueden o podrán derivar estado parcial frente a fallido y rellenar advertencias estructuradas; esta feature define la experiencia y los requisitos de presentación y mensajes, no sustituye la lógica de negocio de extracción.
- El umbral numérico por defecto para “texto muy corto” es **20 palabras**; desviaciones se documentan en el plan y en notas de producto.
- Los límites de tamaño y tipos de archivo admitidos siguen las políticas ya definidas por el producto; aquí solo se exige que el rechazo sea comprensible en interfaz.
- La vista de historial puede estar en desarrollo paralelo; la US de prioridad P3 aplica cuando esa vista exista.
- El idioma único de producto para mensajes y etiquetas cubiertos por esta feature es el **español**; otra lengua sería una ampliación explícita posterior.
- Los detalles técnicos opcionales en interfaz siguen el modelo **colapsado por defecto, expandible por cualquier usuaria**, sin exponer secretos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para el conjunto de escenarios de aceptación definidos en esta especificación (sin participantes, texto corto, fallo de transcripción, tiempo agotado, validación de entrada vacía o archivo inválido), el **100%** de las respuestas visibles a la usuaria final **y**, cuando esos escenarios se cubran vía HTTP, el **100%** de los cuerpos de respuesta pertinentes del contrato público usan lenguaje natural y **ninguno** incluye trazas técnicas ni textos de excepción interna en el recorrido principal de uso.
- **SC-002**: En revisión con checklist de accesibilidad básica (etiquetas de estado), el estado **completado**, **parcial** o **fallido** es identificable leyendo texto en pantalla en el **100%** de las pantallas de resultado cubiertas por esta feature.
- **SC-003**: Cuando exista transcripción completa disponible para la interfaz tras flujo multimedia, una persona puede copiar el texto íntegro al portapapeles mediante la acción dedicada en **un único paso** adicional al pegar en un destino (sin obligar a seleccionar manualmente todo el texto del bloque).
- **SC-004**: En prueba con al menos tres casos (avisos + análisis parcial, solo validación de entrada, fallo sin contenido analítico), observadores no técnicos identifican correctamente en el **90%** o más de los casos qué bloque es “mensaje del sistema” y cuál es “contenido del análisis”, sin breve previo al entrenamiento más allá del uso normal del producto.
