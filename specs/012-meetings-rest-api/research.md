# Research: 012-meetings-rest-api

**Feature**: 012-meetings-rest-api | **Date**: 2026-03-22

## 1. Liveness vs readiness en FastAPI

**Decision**: Mantener `GET /health` como **liveness** (respuesta rápida, sin tocar BD). Añadir `GET /ready` (o `/health/ready`) como **readiness**: ejecutar comprobación mínima de sesión BD (p. ej. `session.exec(select(1))` o equivalente compatible con SQLModel/SQLAlchemy).

**Rationale**: Cumple FR-005 y SC-009; patrón habitual en Kubernetes (liveness/readiness separados); documentar ambos en OpenAPI.

**Alternatives considered**: Un solo `/health` que consulte BD — rechazado en clarificación (opción C: dos comprobaciones). Readiness que llame a proveedores LLM — rechazado por latencia y fragilidad; solo dependencias críticas declaradas (BD para listado/detalle/persist).

## 2. Códigos HTTP para validación vs negocio

**Decision**: Texto vacío tras strip → **422** (ya implementado en `/text`). Payload malformado → 422 (FastAPI). Límite de tamaño texto → **400** (ya implementado). Archivo no permitido / tamaño → **400** o **422** según caso, con `detail` claro en español. No exponer stack traces (FR-007/FR-008).

**Rationale**: Alineado a US-010 y a comportamiento actual; consistente con expectativas de clientes FastAPI.

**Alternatives considered**: Unificar todo en 400 — menos preciso para herramientas que distinguen 422 Unprocessable Entity.

## 3. FR-014: fallo de almacenamiento en GET list / GET detail

**Decision**: En rutas `meetings`, envolver acceso a repositorio/sesión: ante `SQLAlchemyError` / errores de conexión, responder **503 Service Unavailable** (o 500 si se documenta como “error de servidor”) con cuerpo genérico y `detail` humano, **sin** devolver `items: []` ni 404 por id cuando la causa es BD caída.

**Rationale**: Cumple spec y evita falsos negativos operativos.

**Alternatives considered**: Dejar propagar como 500 sin distinguir — válido si se documenta; 503 es más explícito para balanceadores.

## 4. Persistencia tras POST exitoso y coherencia FR-012

**Decision**: Si `graph.invoke` / pipeline completa con respuesta de negocio lista para el cliente pero `persist_graph_success` falla, **no** devolver 200 como éxito completo: responder **503** (o 500) indicando indisponibilidad de persistencia, porque FR-012 exige registro creado cuando la capacidad está activa.

**Rationale**: Evita incumplir SC-007 (listado no refleja lo “exitoso”).

**Alternatives considered**: Loguear y devolver 200 — viola clarificación A y FR-012.

## 5. Identificador en respuesta de procesamiento

**Decision**: Ampliar `ProcessMeetingResponse` con campo opcional `meeting_id: UUID | null` poblado cuando la persistencia crea fila con éxito; `null` si no hubo persistencia (modo sin BD futuro) o fallo antes de crear. Actualizar Gradio/si consume el campo, ignorar si no.

**Rationale**: Mejora integración y verificación directa de SC-007 sin depender solo del listado. El contrato 011 decía “opcional futuro”; 012 eleva la necesidad.

**Alternatives considered**: Solo documentar “buscar en GET /meetings” — más fricción y más lento para automatización.

## 6. OpenAPI / documentación

**Decision**: Confiar en generación automática FastAPI en `/docs` y `/redoc`; asegurar `summary`/`description` en routers y tags (`health`, `process`, `meetings`).

**Rationale**: Cumple FR-009 sin duplicar mantenimiento manual pesado.

**Alternatives considered**: Exportar `openapi.json` versionado en repo — opcional más adelante.
