# PRD: MeetMind — Sistema de Procesamiento de Reuniones con IA

> **Documento de Requisitos del Producto (PRD)**  
> Proyecto: **MeetMind**  
> Fecha: 2025-03-21  
> Versión: 1.0  
> Estado: Borrador inicial  
> Referencia: [ARQUITECTURA-Sistema-Procesamiento-Reuniones.md](./ARQUITECTURA-Sistema-Procesamiento-Reuniones.md)

---

## Índice

- [1. Visión y Objetivos](#1-visión-y-objetivos)
- [2. Descripción del Sistema](#2-descripción-del-sistema)
- [3. Alcance y Scope](#3-alcance-y-scope)
- [4. Entradas del Sistema](#4-entradas-del-sistema)
- [5. Salidas Estructuradas](#5-salidas-estructuradas)
- [6. Arquitectura del Workflow](#6-arquitectura-del-workflow)
- [7. Especificación de Nodos](#7-especificación-de-nodos)
- [8. Requisitos Funcionales](#8-requisitos-funcionales)
- [9. Requisitos No Funcionales](#9-requisitos-no-funcionales)
- [10. Fases de Implementación](#10-fases-de-implementación)
- [11. Criterios de Aceptación](#11-criterios-de-aceptación)
- [12. Consideraciones de Diseño](#12-consideraciones-de-diseño)

---

## 1. Visión y Objetivos

### 1.1 Visión

**MeetMind** es una aplicación de procesamiento automático de reuniones que transforma grabaciones de reuniones o notas desordenadas en documentación empresarial estructurada, utilizando LangGraph y modelos de lenguaje, aplicando capacidades de pensamiento arquitectónico y diseño de workflows.

### 1.2 Objetivos del Proyecto

| Objetivo | Descripción |
|----------|-------------|
| **O1** | Transformar entradas multimedia y textuales en documentación estructurada |
| **O2** | Aplicar metodología de diseño con LangGraph y workflows |
| **O3** | Desarrollar un sistema modular con nodos especializados |
| **O4** | Proporcionar salidas de valor empresarial (minutas, acciones, resúmenes) |

### 1.3 Nota Metodológica

> **Importante**: Este es un proyecto de complejidad considerable. No se espera una implementación completa en la primera iteración, sino un enfoque metodológico en el diseño de la solución. El objetivo principal es desarrollar capacidades de pensamiento arquitectónico y comprensión de workflows con LangGraph.

---

## 2. Descripción del Sistema

### 2.1 ¿Qué es?

**MeetMind** es un sistema de procesamiento automático que ingiere grabaciones de reuniones (audio/video) o notas en texto, y genera documentación empresarial formal mediante un workflow orquestado con LangGraph. Utiliza modelos de lenguaje para extracción de información y generación de artefactos estructurados.

### 2.2 Arquitectura de tres capas

El sistema se organiza en **tres capas** desacopladas:

| Capa | Tecnología | Responsabilidad |
|------|------------|-----------------|
| **Presentación** | Gradio | Interfaz de usuario para carga de archivos, historial de reuniones y visualización de resultados |
| **API** | FastAPI | API REST para orquestar solicitudes, validar entradas y servir el workflow |
| **Negocio** | LangGraph + LangChain | Workflow de procesamiento con nodos especializados |

### 2.3 ¿Para quién?

- **Asistentes/Coordinadores**: Personas que documentan reuniones manualmente
- **Equipos de proyecto**: Que necesitan trazabilidad de acuerdos y acciones
- **Líderes/Gerentes**: Que requieren resúmenes ejecutivos rápidos
- **Contexto**: Empresas tecnológicas, equipos ágiles, consultoría

### 2.4 Problema que resuelve

- Documentación manual de reuniones consume tiempo y es inconsistente
- Información valiosa queda dispersa en grabaciones o notas desordenadas
- Falta de trazabilidad de acuerdos y responsables
- Dificultad para acceder rápidamente a puntos clave de reuniones pasadas

---

## 3. Alcance y Scope

### 3.1 Incluido en el alcance

- Procesamiento de archivos multimedia (audio/video) mediante transcripción
- Procesamiento de documentos de texto (TXT, Markdown)
- Workflow de nodos especializados con LangGraph (incluye preproceso + 5 nodos de extracción/generación)
- Generación de minutas, acciones, temas, participantes y resumen ejecutivo
- Interfaz de selección de archivos (Gradio)
- API REST (FastAPI) para procesamiento y consulta
- Persistencia e historial de reuniones procesadas (consulta posterior por reunión)
- Manejo básico de errores y casos edge

### 3.2 Excluido del alcance (v1)

- Integración con calendarios o herramientas de videoconferencia
- Edición colaborativa de minutas
- Búsqueda semántica en historial de reuniones
- Multi-idioma (español como idioma principal implícito)

---

## 4. Entradas del Sistema

| Tipo | Formatos soportados | Descripción |
|------|---------------------|-------------|
| **Multimedia** | MP4, MOV, MP3, WAV, M4A, WEBM, MKV | Grabaciones de reuniones en audio o video |
| **Documentos** | TXT, Markdown | Notas escritas o transcripciones previas |

### 4.1 Requisitos de entrada

- Archivos deben ser accesibles y legibles por el sistema
- Para multimedia: se requiere capacidad de transcripción (STT)
- Tamaño máximo de archivo: por definir según infraestructura

---

## 5. Salidas Estructuradas

Para cada entrada procesada, el sistema debe generar:

| Salida | Descripción | Restricciones |
|--------|-------------|---------------|
| **Participantes** | Lista identificada de personas que participaron | Nombres separados por comas |
| **Temas principales** | Temas principales discutidos | 3-5 elementos; separados por punto y coma |
| **Acciones acordadas** | Compromisos con responsables asignados | Separadas por pipe (\|) |
| **Minuta formal** | Documento formal estructurado de la reunión | Máximo 150 palabras; tono profesional |
| **Resumen ejecutivo** | Síntesis ultra-concisa | Máximo 30 palabras; enfoque en puntos clave |

---

## 6. Arquitectura del Workflow

### 6.1 Diagrama de flujo

```
START → preprocess (route) → extract_participants → identify_topics → extract_actions → generate_minutes → create_summary → END
```

El nodo **preprocess** determina si la entrada es multimedia (requiere transcripción) o texto, y prepara `raw_text` para el flujo.

### 6.2 Secuencia de nodos

| Orden | Nodo | Descripción |
|-------|------|-------------|
| 0 | preprocess | Enrutamiento: multimedia → transcripción; texto → lectura directa. Produce `raw_text` |
| 1 | extract_participants | Extrae nombres de participantes |
| 2 | identify_topics | Identifica temas principales |
| 3 | extract_actions | Extrae acciones y responsables |
| 4 | generate_minutes | Genera minuta formal |
| 5 | create_summary | Crea resumen ejecutivo |

### 6.3 Dependencias entre nodos

- **preprocess**: Debe ejecutarse primero; produce `raw_text` a partir de la entrada (transcripción o lectura).
- **extract_participants**, **identify_topics**, **extract_actions**: Pueden ejecutarse en paralelo desde el punto de vista lógico (extraen información independiente del texto)
- **generate_minutes**: Depende de participantes, temas y acciones (usa toda la info extraída)
- **create_summary**: Depende de toda la información procesada (incluida la minuta)

---

## 7. Especificación de Nodos

### 7.0 Nodo 0: Preproceso (route)

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Determinar tipo de entrada (multimedia vs texto) y producir `raw_text` |
| **Multimedia** | Invoca transcripción (STT); resultado → `raw_text` |
| **Texto** | Lee contenido de archivo TXT/MD o cuerpo JSON; → `raw_text` |
| **Output** | Estado inicial con `raw_text` y opcionalmente `source_file` |

### 7.1 Nodo 1: Extractor de Participantes

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Identificar nombres de personas en el texto |
| **Desafío técnico** | Distinguir nombres propios de otros términos |
| **Formato de salida** | Lista de nombres separados por comas |
| **Input** | Texto transcrito o notas |

### 7.2 Nodo 2: Analizador de Temas

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Identificar temas principales de discusión |
| **Desafío técnico** | Evitar categorías demasiado generales o específicas |
| **Formato de salida** | Temas separados por punto y coma |
| **Restricción** | 3-5 temas |
| **Input** | Texto transcrito o notas |

### 7.3 Nodo 3: Extractor de Acciones

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Localizar compromisos y asignaciones de responsabilidad |
| **Desafío técnico** | Identificar acciones implícitas versus explícitas |
| **Formato de salida** | Acciones separadas por pipe (\|) |
| **Input** | Texto transcrito o notas |

### 7.4 Nodo 4: Generador de Minutas

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Crear documento formal estructurado |
| **Input** | Información procesada de nodos anteriores (participantes, temas, acciones) |
| **Restricciones** | Máximo 150 palabras; tono profesional |

### 7.5 Nodo 5: Creador de Resumen

| Atributo | Valor |
|----------|-------|
| **Responsabilidad** | Generar síntesis ejecutiva ultra-concisa |
| **Input** | Toda la información procesada |
| **Restricciones** | Máximo 30 palabras; enfoque en puntos clave |

---

## 8. Requisitos Funcionales

### 8.1 RF-01: Procesamiento de archivos multimedia

- **RF-01.1**: El sistema debe soportar transcripción de archivos MP4, MOV, MP3, WAV, M4A, WEBM, MKV
- **RF-01.2**: La transcripción debe producir texto utilizable por los nodos de extracción

### 8.2 RF-02: Procesamiento de documentos de texto

- **RF-02.1**: El sistema debe aceptar archivos TXT y Markdown
- **RF-02.2**: El contenido debe pasarse directamente al workflow sin transcripción

### 8.3 RF-03: Workflow LangGraph

- **RF-03.1**: Implementar grafo con nodo preprocess + 5 nodos especializados en secuencia
- **RF-03.2**: Definir clase State con todos los campos requeridos
- **RF-03.3**: Cada nodo debe procesar su responsabilidad y actualizar el estado

### 8.4 RF-04: Extracción de información

- **RF-04.1**: Extraer participantes (lista separada por comas)
- **RF-04.2**: Extraer 3-5 temas principales (separados por punto y coma)
- **RF-04.3**: Extraer acciones con responsables (separadas por pipe)

### 8.5 RF-05: Generación de documentos

- **RF-05.1**: Generar minuta formal (máx. 150 palabras)
- **RF-05.2**: Generar resumen ejecutivo (máx. 30 palabras)

### 8.6 RF-06: Interfaz y errores

- **RF-06.1**: Interfaz de selección de archivos (Gradio: upload, historial, resultados)
- **RF-06.2**: Manejo de errores y casos donde la información está incompleta o es ambigua

### 8.7 RF-07: API REST

- **RF-07.1**: `POST /api/v1/process/file` — procesar archivo (multipart: audio/video/texto)
- **RF-07.2**: `POST /api/v1/process/text` — procesar texto plano (JSON body)
- **RF-07.3**: `GET /api/v1/meetings` — listar historial de reuniones procesadas
- **RF-07.4**: `GET /api/v1/meetings/{id}` — detalle de una reunión procesada
- **RF-07.5**: `GET /health` — health check

### 8.8 RF-08: Persistencia e historial

- **RF-08.1**: Persistir cada reunión procesada en base de datos (MeetingRecord)
- **RF-08.2**: Asignar identificador único (id) a cada reunión
- **RF-08.3**: Permitir consulta de historial (lista y detalle por id)
- **RF-08.4**: Campos persistidos: participantes, temas, acciones, minuta, resumen, archivo origen, errores, estado (completed | failed | partial), fecha de creación

---

## 9. Requisitos No Funcionales

### 9.1 Tecnología

| Requisito | Especificación |
|-----------|----------------|
| Orquestación | LangGraph para workflow multi-nodo |
| Modelos y prompts | LangChain para LLM, prompts y parsing estructurado |
| API REST | FastAPI (validación Pydantic, async, OpenAPI) |
| UI | Gradio (upload, historial, resultados) |
| Persistencia | SQLModel/SQLAlchemy + SQLite/PostgreSQL para historial |
| Modelos | LLM para extracción y generación (por definir: OpenAI, Anthropic, local) |
| Transcripción | Servicio de Speech-to-Text para multimedia (por definir: Whisper, API cloud) |

### 9.2 Robustez

- **RNF-01**: Manejar inputs de baja calidad (audio con ruido, texto fragmentado)
- **RNF-02**: Estrategias para información incompleta o ambigua
- **RNF-03**: Respuestas degradadas cuando no hay datos suficientes

### 9.3 Mantenibilidad

- **RNF-04**: Modularidad: nodos independientes y testeables
- **RNF-05**: Prompts específicos por nodo para facilitar ajustes

---

## 10. Fases de Implementación

### Fase 1: Estructura Básica

| # | Tarea | Criterio de completitud |
|---|-------|-------------------------|
| 1 | Definir clase State con todos los campos requeridos | State tipado con participantes, temas, acciones, minuta, resumen |
| 2 | Configurar grafo básico de LangGraph sin lógica de negocio | Grafo compilado y ejecutable |
| 3 | Implementar nodo de prueba que procese texto hardcodeado | Nodo retorna datos de prueba |
| 4 | Verificar flujo end-to-end | START → END ejecutado correctamente |

### Fase 2: Nodos Especializados

| # | Tarea | Criterio de completitud |
|---|-------|-------------------------|
| 1 | Desarrollar prompts específicos para cada tipo de extracción | 5 prompts definidos y documentados |
| 2 | Implementar lógica de procesamiento de respuestas del LLM | Parsing de formatos (comas, punto y coma, pipe) |
| 3 | Conectar todos los nodos en el flujo secuencial | Flujo completo funcional |
| 4 | Probar con datos de ejemplo | Validación de calidad de outputs |

### Fase 3: Integración Completa

| # | Tarea | Criterio de completitud |
|---|-------|-------------------------|
| 1 | Implementar nodo preprocess y rutas multimedia vs texto | Enrutamiento funcional |
| 2 | Añadir capacidad de procesamiento de archivos de texto | Carga de TXT/MD vía file_loader |
| 3 | Integrar transcripción de archivos multimedia | Audio/video → texto |
| 4 | Implementar API REST (FastAPI) | Endpoints /process y /meetings operativos |
| 5 | Implementar persistencia y repositorio de reuniones | MeetingRecord en BD; create, get, list |
| 6 | Implementar interfaz Gradio (upload, historial) | UI para subir archivos y consultar reuniones |
| 7 | Añadir manejo de errores y casos edge | Errores capturados y mensajes claros |

---

## 11. Criterios de Aceptación

### 11.1 Criterios globales

- [ ] El sistema procesa al menos un archivo de texto (TXT o MD) y produce las 5 salidas
- [ ] El sistema procesa al menos un archivo multimedia y produce las 5 salidas
- [ ] La minuta no excede 150 palabras
- [ ] El resumen ejecutivo no excede 30 palabras
- [ ] Los temas están entre 3 y 5
- [ ] Las acciones incluyen responsable cuando es identificable
- [ ] Cada reunión procesada se persiste con id único y se puede consultar por historial
- [ ] La API REST responde correctamente en /process y /meetings

### 11.2 Criterios por nodo

- [ ] **Participantes**: Lista coherente de nombres (no términos genéricos)
- [ ] **Temas**: Nivel de granularidad apropiado (ni muy general ni muy específico)
- [ ] **Acciones**: Formato "acción | responsable" o similar cuando aplica
- [ ] **Minuta**: Estructura formal, tono profesional
- [ ] **Resumen**: Puntos clave capturados en 30 palabras o menos

---

## 12. Consideraciones de Diseño

### 12.1 Modularidad del Proceso

**Pregunta**: ¿Un único prompt o múltiples nodos especializados?

**Recomendación**: Múltiples nodos especializados. Ventajas:
- Especialización permite prompts optimizados por tarea
- Facilitación de pruebas unitarias
- Mantenibilidad y ajuste independiente
- Mejor trazabilidad de errores

### 12.2 Secuenciación de Operaciones

**Participantes, temas y acciones**: Independientes entre sí; pueden extraerse en paralelo si se desea optimizar (requiere adaptar el grafo).

**Minuta y resumen**: Dependen de la información extraída; deben ejecutarse después.

### 12.3 Gestión del Estado

**Campos requeridos en State**:

```python
# Propuesta de esquema
participants: list[str]      # o str separado por comas
topics: list[str]            # 3-5 elementos
actions: list[dict]          # {action: str, responsible: str}
minutes: str                 # max 150 palabras
executive_summary: str       # max 30 palabras
raw_text: str                # texto fuente (opcional, para trazabilidad)
```

### 12.4 Robustez ante información incompleta

| Escenario | Estrategia |
|-----------|------------|
| Sin participantes identificables | Retornar lista vacía o "No identificados" |
| Menos de 3 temas | Retornar los disponibles; no forzar relleno artificial |
| Acciones implícitas | Incluir con responsable "Por asignar" si no es identificable |
| Texto muy corto | Advertencia al usuario; outputs con prefijo "[Información limitada]" |
| Audio de baja calidad | Transcripción con marcadores de incertidumbre; LLM puede indicar ambigüedad |

### 12.5 Consideraciones de API y seguridad

| Escenario | Estrategia |
|-----------|------------|
| Transcripción fallida | Añadir a `processing_errors`; retornar estado parcial o HTTP 422 |
| Archivo no soportado | Validación MIME en API; respuesta 400 |
| Texto vacío o muy corto | Validación en API; nodos retornan valores por defecto o "[Información limitada]" |
| Seguridad | Validar tipos MIME y extensiones en uploads; límite de tamaño de archivo configurable |

---

## Anexo A: Campos del Estado (Propuesta)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| raw_text | str | Sí | Texto fuente (transcripción o contenido) |
| participants | str | Sí | Nombres separados por comas |
| topics | str | Sí | Temas separados por punto y coma |
| actions | str | Sí | Acciones separadas por pipe |
| minutes | str | Sí | Minuta formal (max 150 palabras) |
| executive_summary | str | Sí | Resumen (max 30 palabras) |
| source_file | str | No | Nombre del archivo de origen |
| processing_errors | list | No | Errores o advertencias durante el proceso |

### Campos del registro persistido (MeetingRecord)

Además del estado del workflow, el registro en base de datos incluye:

| Campo | Descripción |
|-------|-------------|
| id | Identificador único (UUID) |
| status | Estado: `completed` \| `failed` \| `partial` |
| created_at | Fecha y hora de procesamiento |

---

## Anexo B: Formatos de Salida Esperados

```
participants: "Juan Pérez, María García, Carlos López"
topics: "Presupuesto Q2; Planificación del lanzamiento; Asignación de recursos"
actions: "Revisar propuesta comercial | Juan Pérez | Antes del viernes | Enviar informe de avance | María García | Próxima reunión"
minutes: "[Texto formal de máximo 150 palabras]"
executive_summary: "[Síntesis de máximo 30 palabras]"
```

---

*Documento PRD del proyecto MeetMind. Generado a partir de especificación técnica. Base para User Stories, épicas y tickets de implementación.*
