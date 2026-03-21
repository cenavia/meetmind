<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.1.0
Modified principles: N/A
Added sections: VI. Agent Skills Obligatorias (nuevo principio), tabla de skills en Flujo de Desarrollo
Removed sections: N/A
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Constitution Check references principles by document—no change needed
  - .specify/templates/spec-template.md: ✅ Scope aligned
  - .specify/templates/tasks-template.md: ✅ Task categorization supports skill-driven development
  - .specify/templates/commands/*.md: N/A (folder not present)
Follow-up TODOs: None
-->

# MeetMind Constitution

## Core Principles

### I. Arquitectura de Tres Capas

El sistema MUST mantener una separación estricta de responsabilidades entre capas:

- **Capa de Presentación (Gradio)**: Captura de entrada (archivo o texto), invocación del backend y visualización de resultados. La UI NO debe contener lógica de negocio.
- **Capa de API (FastAPI)**: Validación de entradas, orquestación del workflow LangGraph y respuestas tipadas. La API NO debe conocer la estructura interna del grafo.
- **Capa de Negocio (LangGraph + LangChain)**: Transcripción, extracción y generación mediante nodos especializados. El Core NO debe depender de HTTP ni de la UI.

**Rationale**: La arquitectura documentada en ARQUITECTURA-Sistema-Procesamiento-Reuniones.md define este patrón; desacoplamiento permite evolución independiente, testing por capas y sustitución de componentes (ej. Gradio por otra UI).

### II. Nodos Autocontenidos

Cada nodo del workflow MUST residir en su propia carpeta bajo `agents/<agente>/nodes/<nodo>/`, conteniendo:

- `node.py`: Lógica del nodo.
- `prompt.py`: Prompts específicos (separados para ajustes sin tocar lógica).

Un agente (ej. `meeting`) MUST ser autocontenido con `agent.py`, `state.py`, `nodes/` y `routes/`. Nuevos agentes se añaden como carpetas hermanas sin modificar el existente.

**Rationale**: Facilita tests unitarios por nodo, mantenibilidad, trazabilidad de errores y escalabilidad (batch_summary, etc.) según la arquitectura.

### III. Formatos de Salida Estructurados

Las salidas del workflow MUST cumplir las restricciones del PRD (Anexo A/B):

| Campo               | Formato                          | Restricción                |
|---------------------|----------------------------------|----------------------------|
| participants        | str                              | Nombres separados por coma |
| topics              | str                              | 3-5 elementos; punto y coma|
| actions             | str                              | Separadas por pipe (\|)    |
| minutes             | str                              | Máx. 150 palabras          |
| executive_summary   | str                              | Máx. 30 palabras           |

El esquema de estado (MeetingState) y los modelos Pydantic de la API MUST reflejar estos formatos. Validación de restricciones en los nodos o en la capa API.

**Rationale**: Garantiza interoperabilidad, UX consistente y cumplimiento de criterios de aceptación del PRD.

### IV. Robustez ante Información Incompleta

El sistema MUST manejar casos edge según PRD 12.4 y arquitectura 11.2:

- **Sin participantes identificables**: Retornar `"No identificados"` o lista vacía.
- **Menos de 3 temas**: Retornar los disponibles; NO forzar relleno artificial.
- **Acciones implícitas**: Incluir responsable `"Por asignar"` cuando no sea identificable.
- **Texto muy corto**: Prefijo `[Información limitada]` en salidas relevantes.
- **Transcripción fallida**: Añadir a `processing_errors`, retornar estado parcial o HTTP 422 según contexto.

**Rationale**: Evita fallos en producción con entradas de baja calidad y mejora la experiencia de uso.

### V. Modularidad y Testabilidad

Cada componente MUST ser independiente y testeable:

- **Nodos**: Tests unitarios en `tests/unit/agents/meeting/` (nodos, state).
- **API**: Tests de integración en `tests/integration/` para endpoints.
- **Repositorios/DB**: Tests en `tests/unit/db/`.
- Prompts en módulos dedicados; cambios de prompts NO deben exigir cambios en la lógica del nodo.

La API MUST consumir el grafo compilado vía inyección de dependencias (`Depends`); el grafo debe poder ejecutarse en aislamiento para tests.

**Rationale**: Alineado con RNF-04, RNF-05 del PRD y consideraciones de diseño de la arquitectura.

### VI. Agent Skills Obligatorias

Los agentes de desarrollo (incl. IA asistente) MUST consultar las Agent Skills del proyecto **antes** de implementar código o tomar decisiones de diseño en las tecnologías relacionadas. Las skills definen prácticas recomendadas, patrones y restricciones que previenen errores y mantienen consistencia.

- **Al inicio de proyecto o cambios de arquitectura**: Consultar `framework-selection` antes de elegir LangChain/LangGraph/Deep Agents.
- **Al configurar dependencias**: Consultar `langchain-dependencies` para versiones y paquetes.
- **Al implementar nodos/workflows LangGraph**: Consultar `langgraph-fundamentals`.
- **Al implementar API REST**: Consultar `fastapi`.
- **Al implementar UI**: Consultar `gradio`.
- **Cuando aplique**: Persistencia (`langgraph-persistence`), HITL (`langgraph-human-in-the-loop`), RAG (`langchain-rag`), middleware (`langchain-middleware`), gestión de requisitos (`project-manager`), ideación (`product-ideation-brainstorm`).

Las skills están en `.claude/skills/` y `.agents/skills/`; el archivo `skills-lock.json` lista las versiones bloqueadas. Ignorar esta obligación justifica violaciones documentadas en "Complexity Tracking".

**Rationale**: Las skills encapsulan conocimiento especializado y mejores prácticas; su uso sistemático reduce deuda técnica y desviaciones de estándares.

## Restricciones Tecnológicas

- **Stack obligatorio**: LangGraph (orquestación), LangChain (LLM, prompts, parsing), FastAPI (API), Gradio (UI), SQLModel (persistencia).
- **Persistencia**: Historial de reuniones MUST persistirse en BD (MeetingRecord). El checkpointer de LangGraph es opcional (HITL/reanudación).
- **Seguridad**: Validación MIME en uploads, límite de tamaño de archivo configurable, CORS configurado. NO exponer rutas internas ni secrets en logs.
- **Configuración**: Variables de entorno para API keys, DATABASE_URL, proveedor de transcripción; no hardcodear credenciales.

## Flujo de Desarrollo

- **Estructura de código**: Seguir el árbol de directorios en ARQUITECTURA 8.1 (src/api, src/agents, src/db, src/services, src/ui).
- **Documentación**: PRD y arquitectura en `docs/`; cambios arquitectónicos deben actualizar estos documentos.
- **Revisión**: Los PRs deben verificar cumplimiento de principios; la complejidad debe estar justificada.
- **Agent Skills (Principio VI)**: Consultar la tabla siguiente según el proceso o tecnología implicada.

### Tabla de Agent Skills del Proyecto

| Skill | Proceso / Tecnología | Cuándo invocar |
|-------|----------------------|----------------|
| `framework-selection` | Elección de stack (LangChain/LangGraph/Deep Agents) | Inicio de proyecto, antes de escribir código de agentes |
| `langchain-dependencies` | Configuración, dependencias, versiones | Setup de proyecto, instalación de paquetes |
| `langgraph-fundamentals` | StateGraph, nodos, edges, estado | Cualquier código LangGraph |
| `langchain-fundamentals` | Agentes LangChain, create_agent, tools | Si se usan agentes LangChain (complementario a LangGraph) |
| `langgraph-persistence` | Checkpointer, thread_id, Store | Persistencia de estado, reanudación, HITL |
| `langgraph-human-in-the-loop` | interrupt(), Command(resume=...) | Patrones HITL, aprobación en pasos del grafo |
| `langchain-rag` | Loaders, embeddings, vector stores | Búsqueda semántica en historial (v2+) |
| `langchain-middleware` | HITL, middleware, structured output | Agentes con aprobación o salida estructurada Pydantic |
| `fastapi` | API REST, routers, Pydantic | Endpoints, validación, dependencias |
| `gradio` | UI, componentes, event listeners | Interfaz de usuario |
| `project-manager` | User Stories, épicas, tickets | Gestión de requisitos, backlog (requiere PRD) |
| `product-ideation-brainstorm` | Ideación, visión de producto | Diseño inicial, diferenciadores (no técnico) |

*Ubicación: `.claude/skills/<nombre>/SKILL.md` y `.agents/skills/<nombre>/SKILL.md`. Versiones en `skills-lock.json`.*

## Governance

- Esta constitución prima sobre otras prácticas de desarrollo del proyecto MeetMind.
- Las enmiendas requieren documentación del cambio, justificación y actualización de versionado.
- Política de versionado: MAJOR (cambios incompatibles en principios), MINOR (nuevos principios o secciones), PATCH (clarificaciones, typos).
- Las revisiones de código deben comprobar la conformidad con los principios; las desviaciones deben documentarse en "Complexity Tracking" del plan cuando aplique.
- Usar `docs/ARQUITECTURA-Sistema-Procesamiento-Reuniones.md` y `docs/PRD-Sistema-Procesamiento-Reuniones-IA.md` como guía de implementación.
- Respetar el Principio VI (Agent Skills Obligatorias): verificar que las decisiones técnicas hayan considerado las skills correspondientes.

**Version**: 1.1.0 | **Ratified**: 2025-03-21 | **Last Amended**: 2025-03-21
