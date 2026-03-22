# Research: 011-persist-meeting-records

**Date**: 2026-03-22

## 1. Motor y URL de base de datos

**Decision**: Usar **SQLModel** sobre **SQLAlchemy 2** con URL desde variable de entorno `DATABASE_URL`. Valor por defecto en código o documentación: `sqlite:///./meetmind.db` para desarrollo local.

**Rationale**: La constitución del proyecto exige SQLModel y `MeetingRecord`; SQLite minimiza fricción en dev; PostgreSQL satisface producción cambiando solo la URL.

**Alternatives considered**:

- Solo PostgreSQL: rechazado para dev rápido sin servicio externo.
- ORM distinto (p. ej. raw SQL): rechazado por restricción constitucional.

## 2. ¿Dónde invocar la persistencia (create)?

**Decision**: Desde la **capa API** (`process.py`, `process_file_stream.py`) en el momento en que exista un **resultado terminal** listo para comunicar al cliente: (a) diccionario retornado por `graph.invoke` con los cinco campos de salida; (b) error **terminal** después de haber iniciado el pipeline de negocio (p. ej. transcripción fallida) donde la spec exija registro `failed` con `processing_errors`. No persistir en errores de validación temprana que no constituyen “finalización de procesamiento” (texto vacío, archivo sin nombre, 415 por tipo no soportado) salvo que el producto decida ampliarlo en una iteración.

**Rationale**: Cumple FR-001 y la arquitectura de tres capas; el grafo permanece libre de sesiones DB; un solo lugar de orquestación por código de respuesta.

**Alternatives considered**:

- Nodo final `persist` en LangGraph: rechazado — acopla el grafo a infraestructura y dificulta tests aislados.
- Persistir solo en rutas síncronas y no en SSE: rechazado — la UI usa SSE; debe haber paridad de trazabilidad.

## 3. Mapeo de `status` y `processing_errors`

**Decision**:

- Tras `invoke` exitoso: `completed` por defecto; `partial` si en el futuro el estado incluye `processing_errors` no vacío o marcadores explícitos de salida limitada (PRD 12.4); hasta que exista ese campo en el estado, se puede inferir `partial` heurísticamente (p. ej. prefijo `[Información limitada]` en minuta/resumen) o mantener `completed` y documentar la limitación en tasks — **preferir** añadir `processing_errors: str | None` opcional a `MeetingState` y poblarlo en nodos cuando aplique, para alinear con constitución IV.
- Tras fallo de transcripción (sin `invoke`): `failed`, `processing_errors` = mensaje de error legible; demás campos de resultado como cadenas vacías o nulas según el modelo.

**Rationale**: Alineado con FR-003, FR-004 y edge cases de la spec.

**Alternatives considered**:

- Solo `completed` para todo éxito HTTP 200: rechazado — contradice estados parcial/fallido de la spec.

## 4. Migraciones (Alembic)

**Decision**: **MVP**: `create_all` en arranque o función de init documentada para SQLite. **Seguimiento**: introducir Alembic cuando haya más de una revisión de esquema en entornos compartidos (mencionado en US-012).

**Rationale**: Velocidad de entrega; la constitución no exige Alembic en el primer merge.

**Alternatives considered**:

- Alembic desde el primer commit: válido pero más costo; se difiere.

## 5. Contrato de lectura y seguridad

**Decision**: Endpoints REST documentados en `contracts/meetings-api.md`; sin cabeceras de auth en esta feature. Advertencia operativa: no exponer la API a redes no confiables sin proxy/auth.

**Rationale**: FR-009 y clarificaciones de spec.

**Alternatives considered**: API key mínima — fuera de alcance explícito.

## 6. Campo resumen vs `executive_summary`

**Decision**: En BD y contratos persistidos usar nombre **`executive_summary`** (coherente con API actual) o **`summary`** si se prefiere nombre corto en tabla — **recomendación**: columna `executive_summary` para evitar drift con `ProcessMeetingResponse`.

**Rationale**: Una sola fuente de nombres con el modelo de respuesta existente.

**Alternatives considered**: Renombrar API a `summary`: rechazado — rompe clientes y docs previos.
