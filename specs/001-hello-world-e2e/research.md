# Research: Hello World E2E

**Feature**: 001-hello-world-e2e | **Date**: 2025-03-21

## Objetivo

Resolver NEEDS CLARIFICATION del Technical Context y documentar decisiones técnicas para la implementación.

## Decisiones

### 1. Stack y dependencias (ya definidos en PRD/Arquitectura)

**Decision**: Python 3.11+, FastAPI, Gradio, LangGraph, LangChain, uv.

**Rationale**: El PRD y ARQUITECTURA-Sistema-Procesamiento-Reuniones.md establecen el stack. La Constitución (Restricciones Tecnológicas) lo confirma. US-000 especifica uv como gestor.

**Alternatives considered**: pip/poetry — rechazados; US-000 exige uv para reproducibilidad.

---

### 2. Estructura mínima del grafo LangGraph

**Decision**: StateGraph con dos nodos: `preprocess` (normaliza raw_text) y `mock_result` (retorna datos hardcodeados). Sin checkpointer, sin LLM.

**Rationale**: Valida la integración API ↔ grafo sin depender de API keys ni servicios externos. LangGraph permite grafo mínimo sin nodos LLM; el state se actualiza con valores fijos.

**Alternatives considered**:
- Grafo con 5 nodos reales + LLM: bloquea validación en máquinas sin OPENAI_API_KEY.
- Un solo nodo: preprocess aporta limpieza básica y prepara el patrón para nodos reales.

---

### 3. Invocación UI → API

**Decision**: La UI (Gradio) invoca la API por HTTP con `httpx`. URL base desde `API_BASE_URL` (default `http://localhost:8000`).

**Rationale**: Clarificación de spec (Q2): validación completa de capas. Coincide con Opción A de la arquitectura (Gradio llama a la API).

**Alternatives considered**: Invocar grafo directamente (Opción B): rechazado por spec.

---

### 4. Formato de respuesta estructurada

**Decision**: JSON con campos: `participants`, `topics`, `actions`, `minutes`, `executive_summary` (nombres en snake_case en API). Valores tipo string según Constitución III.

**Rationale**: Constitución y PRD definen los campos. Para Hello World, valores mock en formato final permiten validar contrato.

**Alternatives considered**: Cambiar a camelCase: rechazado; la API FastAPI usa convención snake_case por defecto.

---

### 5. Límite de longitud y validación

**Decision**: Límite 50.000 caracteres en API. Validación en capa API con Pydantic; respuesta 400 con `{"detail": "Texto excede el límite de 50000 caracteres"}` (o similar).

**Rationale**: Clarificación de spec (Q3). 50k caracteres cubre reuniones largas; evita timeouts en modo mock.

---

### 6. Estado de carga en Gradio

**Decision**: Usar `gr.Button` con estado loading nativo (`variant="primary"`) o deshabilitar botón durante la petición; añadir indicador visual (ej. "Procesando...") en el output antes de mostrar resultado.

**Rationale**: Clarificación de spec (Q4). Gradio ofrece `show_progress` o estado del botón; la opción más simple cumple el requisito.

---

### 7. Documentación de ejecución

**Decision**: Actualizar `docs/planning/COMO-EJECUTAR.md` con: `uv sync`, comandos para API y UI, verificación de health, variable `API_BASE_URL`.

**Rationale**: FR-006 y US-000. El documento ya existe; se complementa con las variables de entorno definidas en spec.
