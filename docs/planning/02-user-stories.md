# User Stories — MeetMind

> Basado en PRD v1.0 | Proyecto MeetMind

---

## US-001: Procesar grabación multimedia

**Como** Marina (asistente) o Pablo (desarrollador)  
**Quiero** subir una grabación de reunión (audio o video)  
**Para** obtener documentación estructurada sin transcribir manualmente

### Criterios de Aceptación

- [ ] El sistema acepta archivos MP4, MOV, MP3, WAV, M4A, WEBM, MKV
- [ ] La transcripción se ejecuta automáticamente y produce texto utilizable
- [ ] El workflow genera participantes, temas, acciones, minuta y resumen ejecutivo
- [ ] El usuario recibe feedback durante el procesamiento

### Notas Técnicas

- Integración con servicio STT (Whisper u otro)
- Nodo `preprocess` detecta multimedia y dispara transcripción

---

## US-002: Procesar notas en texto

**Como** Marina o Pablo  
**Quiero** subir un archivo de texto (TXT o Markdown) con notas de reunión  
**Para** obtener documentación estructurada sin transcripción

### Criterios de Aceptación

- [ ] El sistema acepta archivos TXT y Markdown
- [ ] El contenido pasa directamente al workflow sin transcripción
- [ ] Se generan las 5 salidas estructuradas (participantes, temas, acciones, minuta, resumen)
- [ ] Se respeta el formato y encoding del archivo

### Notas Técnicas

- Nodo `preprocess` detecta texto y lee contenido directamente
- File loader para TXT/MD

---

## US-003: Ver extracción de participantes

**Como** Ricardo (líder de proyecto)  
**Quiero** ver la lista de participantes identificados en la reunión  
**Para** saber quién estuvo presente y asignar responsabilidades

### Criterios de Aceptación

- [ ] Los participantes se muestran como lista de nombres separados por comas
- [ ] No se incluyen términos genéricos como "persona" o "alguien"
- [ ] Si no hay participantes identificables, se muestra lista vacía o "No identificados"
- [ ] Los nombres son coherentes con el contexto de la reunión

### Notas Técnicas

- Nodo `extract_participants` con prompt especializado
- Salida en campo `participants` del State

---

## US-004: Ver temas principales discutidos

**Como** Elena (gerente) o Ricardo  
**Quiero** ver los temas principales de la reunión  
**Para** entender el alcance de la discusión sin revisar todo el contenido

### Criterios de Aceptación

- [ ] Se muestran entre 3 y 5 temas principales
- [ ] Los temas tienen nivel de granularidad apropiado (ni muy general ni muy específico)
- [ ] Se muestran separados por punto y coma
- [ ] Si hay menos de 3 temas identificables, se retornan los disponibles sin forzar relleno

### Notas Técnicas

- Nodo `identify_topics`
- Restricción 3–5 en prompt; no forzar si hay menos datos

---

## US-005: Ver acciones acordadas con responsables

**Como** Ricardo o Pablo  
**Quiero** ver las acciones acordadas con su responsable asignado  
**Para** dar seguimiento a compromisos y trazabilidad

### Criterios de Aceptación

- [ ] Las acciones incluyen responsable cuando es identificable
- [ ] Formato "acción | responsable" o similar
- [ ] Si el responsable no es identificable, se muestra "Por asignar"
- [ ] Las acciones implícitas se incluyen con la mejor estimación posible
- [ ] Salida separada por pipe (|)

### Notas Técnicas

- Nodo `extract_actions`
- Parsing de formato pipe para estructurar datos

---

## US-006: Ver minuta formal

**Como** Marina o Ricardo  
**Quiero** obtener una minuta formal estructurada de la reunión  
**Para** compartir documentación profesional con stakeholders

### Criterios de Aceptación

- [ ] La minuta tiene máximo 150 palabras
- [ ] Tono profesional y estructura formal
- [ ] Incluye la información de participantes, temas y acciones procesados
- [ ] Es legible y coherente con el contenido original

### Notas Técnicas

- Nodo `generate_minutes`
- Depende de la salida de extract_participants, identify_topics, extract_actions

---

## US-007: Ver resumen ejecutivo

**Como** Elena (gerente)  
**Quiero** ver un resumen ejecutivo ultra-conciso  
**Para** captar los puntos clave en segundos sin leer la minuta completa

### Criterios de Aceptación

- [ ] El resumen tiene máximo 30 palabras
- [ ] Enfocado en puntos clave y decisiones
- [ ] Permite decidir si profundizar en la minuta completa
- [ ] Síntesis clara y accionable

### Notas Técnicas

- Nodo `create_summary`
- Depende de toda la información procesada (incluida la minuta)

---

## US-008: Subir archivos desde la interfaz web

**Como** Marina o Pablo  
**Quiero** usar una interfaz web para subir archivos  
**Para** procesar reuniones sin usar la línea de comandos ni la API directamente

### Criterios de Aceptación

- [ ] Interfaz de carga (upload) para archivos multimedia y texto
- [ ] Feedback visual durante la carga y procesamiento
- [ ] Visualización de resultados (participantes, temas, acciones, minuta, resumen)
- [ ] Validación de tipos de archivo soportados
- [ ] Mensajes de error claros si el archivo no es válido

### Notas Técnicas

- Gradio: componentes de upload, display de resultados
- Integración con API backend

---

## US-009: Consultar historial de reuniones procesadas

**Como** Ricardo o Elena  
**Quiero** ver el historial de reuniones procesadas  
**Para** acceder a documentación pasada sin volver a procesar

### Criterios de Aceptación

- [ ] Lista de reuniones procesadas con identificación única (id)
- [ ] Vista de detalle de cada reunión (participantes, temas, acciones, minuta, resumen)
- [ ] Información de archivo origen y fecha de procesamiento
- [ ] Estado de cada reunión (completed | failed | partial)
- [ ] Acceso desde la interfaz Gradio y/o API

### Notas Técnicas

- Persistencia MeetingRecord en BD
- Endpoints GET /meetings y GET /meetings/{id}

---

## US-010: Procesar reuniones vía API REST

**Como** Pablo (desarrollador) o integrador de sistemas  
**Quiero** procesar reuniones mediante API REST  
**Para** integrar MeetMind con otros sistemas o automatizar flujos

### Criterios de Aceptación

- [ ] POST /api/v1/process/file: procesar archivo (multipart)
- [ ] POST /api/v1/process/text: procesar texto plano (JSON body)
- [ ] GET /api/v1/meetings: listar historial
- [ ] GET /api/v1/meetings/{id}: detalle de reunión
- [ ] GET /health: health check
- [ ] Respuestas con códigos HTTP adecuados (400, 422, 500)
- [ ] Documentación OpenAPI disponible

### Notas Técnicas

- FastAPI, validación Pydantic
- Manejo de errores y validación MIME

---

## US-011: Recibir feedback ante información incompleta o errores

**Como** Marina o cualquier usuario  
**Quiero** recibir mensajes claros cuando la información es incompleta o hay errores  
**Para** entender qué pasó y qué puedo hacer al respecto

### Criterios de Aceptación

- [ ] Mensajes claros cuando no se identifican participantes
- [ ] Advertencia cuando el texto es muy corto o de baja calidad
- [ ] Estado "partial" cuando hay resultados parciales
- [ ] Estado "failed" con descripción del error cuando falla el procesamiento
- [ ] Campos processing_errors para advertencias o errores
- [ ] No se muestran errores técnicos crudos al usuario final

### Notas Técnicas

- Estrategias de robustez en cada nodo
- Validación en API (texto vacío, archivo no soportado, transcripción fallida)

---

## US-012: Almacenar reuniones procesadas de forma persistente

**Como** sistema  
**Quiero** persistir cada reunión procesada en base de datos  
**Para** permitir consulta posterior y trazabilidad

### Criterios de Aceptación

- [ ] Cada reunión recibe id único (UUID)
- [ ] Se guardan: participantes, temas, acciones, minuta, resumen, archivo origen
- [ ] Se guardan: status (completed | failed | partial), created_at, processing_errors
- [ ] Operaciones create, get, list funcionan correctamente
- [ ] Los datos persisten entre reinicios de la aplicación

### Notas Técnicas

- SQLModel/SQLAlchemy + SQLite o PostgreSQL
- Repositorio de MeetingRecord
