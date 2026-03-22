# Feature Specification: Ver resumen ejecutivo

**Feature Branch**: `007-executive-summary`  
**Created**: 2026-03-21  
**Status**: Draft  
**Input**: US-007 — Ver un resumen ejecutivo ultra-conciso para captar los puntos clave en segundos sin leer la minuta completa

## Clarifications

### Session 2026-03-21

- Q: ¿Cómo debe definirse y validarse el conteo de palabras del resumen (máximo 30)? → A: Igual que en 006: split por espacios (secuencias de caracteres separadas por espacios en blanco)
- Q: ¿En qué momento se desactiva el botón «Procesar»? → A: Inmediatamente al hacer clic (antes de que termine el procesamiento)
- Q: ¿Cuál debe ser la salida del resumen cuando no hay participantes, temas ni acciones extraídos? → A: Mensaje fijo estándar breve (ej.: "Resumen: No se identificó información procesable en la reunión.")
- Q: ¿En qué idioma debe generarse el resumen ejecutivo? → A: Siempre español
- Q: Si el modelo genera un resumen que supera las 30 palabras, ¿cómo debe manejarse? → A: Re-pedir al modelo que acorte (retry con prompt ajustado) hasta cumplir el límite

## Assumptions

- Existe un flujo de procesamiento previo que genera la minuta (US-006) y toda la información procesada (participantes, temas, acciones).
- El resumen se genera al final del pipeline, utilizando toda la información disponible incluida la minuta.
- La interfaz incluye botones «Procesar» y «Limpiar» para el flujo de carga y procesamiento de archivos.
- Elena (gerente) es el usuario principal que requiere visión ejecutiva en pocas palabras.

## Out of Scope

- Personalización del límite de palabras del resumen.
- Resumen en otros idiomas distintos del español (asumido del contexto MeetMind).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resumen ejecutivo de reunión con decisiones (Priority: P1)

Como Elena (gerente), quiero ver un resumen ejecutivo ultra-conciso que sintetice decisiones, acciones críticas y conclusiones principales, para captar los puntos clave en segundos sin leer la minuta completa.

**Why this priority**: Es el flujo principal; el resumen es la entrada rápida que permite a Elena decidir si profundizar en la minuta completa.

**Independent Test**: Dado un conjunto de participantes, temas, acciones y minuta ya generados, verificar que la salida es un resumen de máximo 30 palabras enfocado en decisiones y acciones clave.

**Acceptance Scenarios**:

1. **Given** la reunión incluyó decisiones y acciones, **When** el sistema genera el resumen ejecutivo, **Then** el resumen tiene máximo 30 palabras
2. **Given** la reunión incluyó decisiones y acciones, **When** el sistema genera el resumen, **Then** destaca decisiones y acciones clave
3. **Given** el resumen generado, **When** Elena lo lee, **Then** puede decidir si leer la minuta completa
4. **Given** el resumen, **When** se revisa, **Then** es síntesis clara y accionable

---

### User Story 2 - Resumen de reunión informativa (Priority: P1)

Como Elena, quiero que cuando la reunión fue principalmente informativa, el resumen sintetice los temas principales manteniendo tono profesional.

**Why this priority**: Cubre el caso donde no hay decisiones explícitas pero sí valor en la síntesis.

**Independent Test**: Dada una reunión informativa, verificar que el resumen sintetiza los temas principales con tono profesional.

**Acceptance Scenarios**:

1. **Given** la reunión fue principalmente informativa, **When** el sistema genera el resumen, **Then** sintetiza los temas principales
2. **Given** el resumen informativo, **When** se revisa, **Then** mantiene tono profesional

---

### User Story 3 - Botón Procesar desactivado hasta Limpiar (Priority: P1)

Como Elena, quiero que tras cargar el archivo y hacer clic en «Procesar», el botón Procesar se desactive hasta que haga clic en «Limpiar», para evitar procesamientos repetidos accidentales.

**Why this priority**: Es un requisito explícito de la US y afecta la usabilidad y prevención de errores de uso.

**Independent Test**: Cargar archivo, hacer clic en Procesar, verificar que el botón Procesar está desactivado; hacer clic en Limpiar y verificar que Procesar vuelve a activarse (si aplica para nuevo procesamiento).

**Acceptance Scenarios**:

1. **Given** Elena ha cargado un archivo de notas, **When** hace clic en «Procesar», **Then** el botón «Procesar» se desactiva
2. **Given** el botón «Procesar» está desactivado tras procesar, **When** Elena hace clic en «Limpiar», **Then** el botón «Procesar» vuelve a activarse para permitir un nuevo procesamiento

---

### Edge Cases

- ¿Qué pasa cuando la reunión no tiene decisiones ni acciones claras? El sistema debe generar un resumen que sintetice los temas principales o indique ausencia de conclusiones accionables.
- ¿Qué pasa cuando no hay participantes, temas ni acciones extraídos? El sistema MUST mostrar un mensaje fijo estándar breve (ej.: "Resumen: No se identificó información procesable en la reunión."), alineado con 006-generate-minutes.
- ¿Qué pasa si el contenido procesado excede lo que cabe en 30 palabras o el modelo genera más de 30 palabras? El sistema debe re-pedir al modelo que acorte (retry con prompt ajustado) hasta cumplir el límite, priorizando coherencia y decisiones/acciones/conclusiones.
- ¿Qué pasa si el usuario hace clic en Procesar sin haber cargado archivo? El comportamiento depende del flujo existente; esta feature asume que el botón solo es relevante cuando hay archivo cargado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar un resumen ejecutivo de máximo 30 palabras a partir de la información procesada (incluida la minuta). El conteo de palabras se define por split por espacios (secuencias separadas por espacios en blanco), alineado con 006-generate-minutes. El resumen se genera siempre en español. Si el modelo excede 30 palabras, se MUST re-pedir acortamiento (retry con prompt ajustado) hasta cumplir el límite.
- **FR-002**: El resumen MUST enfocarse en: decisiones tomadas, acciones críticas, conclusiones principales.
- **FR-003**: El resumen MUST ser síntesis clara y accionable que permita decidir si profundizar en la minuta completa.
- **FR-004**: Para reuniones informativas, el resumen MUST sintetizar los temas principales manteniendo tono profesional.
- **FR-008**: Cuando no hay participantes, temas ni acciones extraídos, el sistema MUST devolver un mensaje fijo estándar breve (ej.: "Resumen: No se identificó información procesable en la reunión.").
- **FR-005**: El botón «Procesar» MUST desactivarse inmediatamente al hacer clic (antes de que termine el procesamiento), tras haber cargado archivo.
- **FR-006**: El botón «Procesar» MUST permanecer desactivado hasta que el usuario haga clic en «Limpiar».
- **FR-007**: Tras hacer clic en «Limpiar», el botón «Procesar» MUST volver a activarse para permitir nuevo procesamiento.

### Key Entities

- **Resumen ejecutivo (summary)**: Texto de máximo 30 palabras que sintetiza decisiones, acciones críticas y conclusiones de la reunión. Permite a Elena captar lo esencial sin leer la minuta completa.
- **Estado de UI (Procesar/Limpiar)**: Estados que determinan si el botón Procesar está habilitado o deshabilitado; Limpiar restablece el flujo para un nuevo procesamiento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Elena puede captar los puntos clave de la reunión en menos de 10 segundos leyendo solo el resumen.
- **SC-002**: El 100% de los resúmenes generados cumplen el límite de 30 palabras.
- **SC-003**: El botón Procesar se desactiva correctamente tras procesar y no permite clics repetidos hasta que se use Limpiar.
- **SC-004**: Elena puede decidir con confianza si necesita leer la minuta completa basándose únicamente en el resumen.
