# User Personas — MeetMind

> Basado en PRD v1.0 | Proyecto MeetMind

---

## Persona 1: Marina — Asistente/Coordinadora

- **Rol:** Asistente ejecutiva o coordinadora de equipos que documenta reuniones manualmente.
- **Necesidades:**
  - Reducir el tiempo dedicado a escribir minutas y actas.
  - Mantener un estándar consistente en la documentación.
  - Poder consultar reuniones pasadas de forma rápida.
- **Pain Points:**
  - Las minutas manuales consumen 30–60 minutos por reunión.
  - Inconsistencia de formato entre reuniones y autores.
  - Información valiosa dispersa en grabaciones o notas desordenadas.

---

## Persona 2: Ricardo — Líder de Equipo / Project Manager

- **Rol:** Líder de proyecto que necesita trazabilidad de acuerdos y acciones.
- **Necesidades:**
  - Seguimiento claro de quién debe hacer qué y para cuándo.
  - Resúmenes rápidos sin revisar grabaciones completas.
  - Historial de reuniones para auditoría y reportes.
- **Pain Points:**
  - Falta de trazabilidad de acuerdos y responsables.
  - Dificultad para recordar compromisos de reuniones anteriores.
  - Tiempo excesivo revisando grabaciones para recuperar un punto concreto.

---

## Persona 3: Elena — Gerente / Directora

- **Rol:** Ejecutiva que requiere visión ejecutiva sin profundizar en detalles.
- **Necesidades:**
  - Resúmenes ejecutivos de pocas palabras.
  - Acceso rápido a temas principales y decisiones tomadas.
  - Evitar escuchar o leer grabaciones completas.
- **Pain Points:**
  - No tiene tiempo para revisar minutas largas.
  - Necesita síntesis que le permitan decidir si profundizar o no.
  - Información clave enterrada en documentos extensos.

---

## Persona 4: Pablo — Desarrollador / Consultor técnico

- **Rol:** Profesional técnico en equipos ágiles o consultoría.
- **Necesidades:**
  - Documentar decisiones técnicas de reuniones.
  - Tener referencias claras de acuerdos (formatos, fechas, responsables).
  - Procesar tanto grabaciones como notas en texto.
- **Pain Points:**
  - Las notas tomadas durante reuniones suelen estar desordenadas.
  - Grabaciones de stand-ups o retrospectivas sin documentación posterior.
  - Dificultad para compartir resultados con el resto del equipo.

---

## Resumen de Requisitos del Producto

### Funcionales

1. Procesar archivos multimedia (MP4, MOV, MP3, WAV, M4A, WEBM, MKV) mediante transcripción.
2. Procesar documentos de texto (TXT, Markdown) sin transcripción.
3. Extraer participantes, temas principales (3–5), y acciones con responsables.
4. Generar minuta formal (máx. 150 palabras) y resumen ejecutivo (máx. 30 palabras).
5. Interfaz Gradio para carga de archivos, historial y visualización de resultados.
6. API REST para procesamiento y consulta de reuniones.
7. Persistir cada reunión procesada con id único y permitir consulta por historial.
8. Manejo de errores y casos donde la información está incompleta o ambigua.

### No Funcionales

- **Seguridad:** Validación de tipos MIME y extensiones en uploads; límite de tamaño configurable.
- **Performance:** Manejo de inputs de baja calidad (audio con ruido, texto fragmentado).
- **Escalabilidad:** Arquitectura modular con nodos independientes y testeables.
- **Mantenibilidad:** Prompts específicos por nodo para facilitar ajustes.
