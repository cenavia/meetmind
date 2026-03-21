# Plantilla de Ticket Técnico

Cada ticket representa una unidad de trabajo con **máximo 3 horas de esfuerzo**.

## Regla de Oro

> Si una tarea requiere más de 3 horas, **DEBE dividirse** en múltiples tickets.

## Plantilla Estándar

```markdown
## Ticket: {PROJ-XXX}

**Título:** {Título descriptivo y conciso}
**Tipo:** [FEATURE] | [BUG] | [TASK] | [SPIKE] | [IMPROVEMENT]
**Estimación:** {1h | 2h | 3h}
**Prioridad:** {Crítica | Alta | Media | Baja}
**Asignado a:** {nombre o "Sin asignar"}
**Sprint:** {número de sprint o "Backlog"}

---

### Descripción

{Descripción clara y completa del trabajo a realizar.
Incluir contexto suficiente para que el desarrollador sea autónomo.}

### User Story Relacionada

**Como** {persona/rol}
**Quiero** {funcionalidad}
**Para** {beneficio}

---

### Criterios de Aceptación

- [ ] {Criterio verificable 1}
- [ ] {Criterio verificable 2}
- [ ] {Criterio verificable 3}
- [ ] Tests unitarios implementados
- [ ] Documentación actualizada (si aplica)

---

### Especificación Técnica

#### Endpoints (si aplica)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/v1/resource` | Obtener recursos |
| POST | `/api/v1/resource` | Crear recurso |

#### Campos/Modelo (si aplica)

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| id | UUID | Sí | Identificador único |
| name | String | Sí | Nombre del recurso |

#### Archivos a Modificar

- `src/components/Feature.tsx` - Componente principal
- `src/api/resource.ts` - Cliente API
- `src/types/resource.ts` - Tipos TypeScript

---

### Tareas Técnicas

1. [ ] {Tarea específica 1}
2. [ ] {Tarea específica 2}
3. [ ] {Tarea específica 3}
4. [ ] {Escribir tests}
5. [ ] {Code review}

---

### Dependencias

- **Bloqueado por:** {PROJ-XXX, PROJ-YYY o "Ninguno"}
- **Bloquea a:** {PROJ-ZZZ o "Ninguno"}
- **Relacionado con:** {PROJ-AAA}

---

### Requisitos No Funcionales

- **Seguridad:** {requisitos de seguridad si aplica}
- **Performance:** {requisitos de rendimiento si aplica}
- **Accesibilidad:** {requisitos a11y si aplica}

---

### Notas Adicionales

{Cualquier información adicional relevante, links a documentación, 
decisiones de diseño, consideraciones especiales, etc.}
```

## Tipos de Ticket

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `[FEATURE]` | Nueva funcionalidad | Implementar filtros de búsqueda |
| `[BUG]` | Corrección de error | Fix error en validación de formulario |
| `[TASK]` | Trabajo técnico | Configurar CI/CD pipeline |
| `[SPIKE]` | Investigación | Evaluar opciones de autenticación |
| `[IMPROVEMENT]` | Mejora existente | Optimizar queries de base de datos |

## Estimación de Esfuerzo

| Horas | Complejidad | Ejemplo |
|-------|-------------|---------|
| 1h | Trivial | Cambio de texto, ajuste de estilo |
| 2h | Simple | CRUD básico, componente simple |
| 3h | Moderada | Feature completa pequeña, integración |
| >3h | **DIVIDIR** | Crear múltiples tickets |

## Ejemplo de División

### Ticket Original (>3h)
"Implementar sistema completo de autenticación"

### Tickets Divididos (≤3h cada uno)
1. `[TASK]` Configurar librería de auth - 2h
2. `[FEATURE]` Endpoint de login - 3h
3. `[FEATURE]` Endpoint de registro - 3h
4. `[FEATURE]` UI de formulario login - 2h
5. `[FEATURE]` UI de formulario registro - 2h
6. `[TASK]` Tests de integración auth - 3h

## Especificación BDD Asociada

Cada ticket con tipo `[FEATURE]` debe incluir escenarios BDD:

```gherkin
Feature: {descripción de la feature}
  Como {rol}
  Quiero {funcionalidad}
  Para {beneficio}

  Scenario: {escenario exitoso}
    Given {precondición}
    When {acción del usuario}
    Then {resultado esperado}

  Scenario: {escenario de error}
    Given {precondición}
    When {acción incorrecta}
    Then {mensaje de error esperado}
```

## Checklist de Calidad del Ticket

Antes de crear el ticket, verificar:

- [ ] Título claro y descriptivo
- [ ] Estimación ≤ 3 horas
- [ ] Criterios de aceptación verificables
- [ ] Dependencias identificadas
- [ ] Archivos a modificar listados
- [ ] Requisitos no funcionales considerados
- [ ] Información suficiente para autonomía del desarrollador
