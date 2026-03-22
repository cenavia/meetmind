# User Stories — MeetMind

> Índice de User Stories del proyecto MeetMind | Basado en PRD v1.0

---

## Resumen

Cada user story está documentada en un archivo independiente enriquecido con:

- **Metadatos:** prioridad, dependencias, estimación
- **Descripción ampliada** de la funcionalidad
- **Criterios de aceptación** con checkboxes
- **Especificación BDD** (Gherkin)
- **Archivos a crear/modificar** según arquitectura
- **Personas vinculadas** del documento de personas
- **Notas técnicas** de implementación

---

## Índice de User Stories

| ID | Título | Prioridad | Archivo |
|----|--------|-----------|---------|
| US-000 | Estructura inicial del proyecto y Hello World end-to-end | P0 | [US-000.md](./US-000.md) |
| US-001 | Procesar grabación multimedia | P2 | [US-001.md](./US-001.md) |
| US-002 | Procesar notas en texto | P1 | [US-002.md](./US-002.md) |
| US-003 | Ver extracción de participantes | P1 | [US-003.md](./US-003.md) |
| US-004 | Ver temas principales discutidos | P1 | [US-004.md](./US-004.md) |
| US-005 | Ver acciones acordadas con responsables | P1 | [US-005.md](./US-005.md) |
| US-006 | Ver minuta formal | P1 | [US-006.md](./US-006.md) |
| US-007 | Ver resumen ejecutivo | P1 | [US-007.md](./US-007.md) |
| US-008 | Subir archivos desde la interfaz web | P2 | [US-008.md](./US-008.md) |
| US-009 | Consultar historial de reuniones procesadas | P2 | [US-009.md](./US-009.md) |
| US-010 | Procesar reuniones vía API REST | P2 | [US-010.md](./US-010.md) |
| US-011 | Recibir feedback ante información incompleta o errores | P2 | [US-011.md](./US-011.md) |
| US-012 | Almacenar reuniones procesadas de forma persistente | P1 | [US-012.md](./US-012.md) |

---

## Orden de implementación sugerido

### Fase 0: Estructura Inicial (P0)
- [US-000](./US-000.md) — Estructura + Hello World E2E

### Fase 1: Workflow Core (P1)
1. [US-012](./US-012.md) — Persistencia
2. [US-002](./US-002.md) — Procesamiento de texto
3. [US-003](./US-003.md) — Extracción de participantes
4. [US-004](./US-004.md) — Identificación de temas
5. [US-005](./US-005.md) — Extracción de acciones
6. [US-006](./US-006.md) — Generación de minuta
7. [US-007](./US-007.md) — Resumen ejecutivo

### Fase 2: API e Integración (P2)
8. [US-010](./US-010.md) — API REST
9. [US-001](./US-001.md) — Procesamiento multimedia
10. [US-008](./US-008.md) — Interfaz Gradio
11. [US-009](./US-009.md) — Historial en UI
12. [US-011](./US-011.md) — Manejo de errores

---

## Dependencias entre User Stories

```
US-000 ──┬──► US-012 ──► US-009
         ├──► US-002 ──┬──► US-003 ─┐
         │             ├──► US-004 ─┼──► US-006 ──► US-007
         │             └──► US-005 ─┘       │
         └──► US-010 ──► US-008             └──► US-011

US-001 ──► (workflow) ──► US-003, 004, 005, 006, 007
```

---

## Referencias

- [PRD del proyecto](../../PRD-Sistema-Procesamiento-Reuniones-IA.md)
- [Arquitectura del sistema](../../ARQUITECTURA-Sistema-Procesamiento-Reuniones.md)
- [User Personas](../01-user-personas.md)
- [Backlog priorizado](../03-backlog-priorizado.md)
