# User Stories — MeetMind

> Basado en PRD v1.0 | Proyecto MeetMind

---

## Índice de User Stories

Las user stories están separadas en archivos independientes enriquecidos en el directorio [`docs/planning/user-stories/`](./user-stories/):

| ID | Título | Prioridad |
|----|--------|-----------|
| [US-000](./user-stories/US-000.md) | Estructura inicial y Hello World E2E | P0 |
| [US-001](./user-stories/US-001.md) | Procesar grabación multimedia | P2 |
| [US-002](./user-stories/US-002.md) | Procesar notas en texto | P1 |
| [US-003](./user-stories/US-003.md) | Ver extracción de participantes | P1 |
| [US-004](./user-stories/US-004.md) | Ver temas principales discutidos | P1 |
| [US-005](./user-stories/US-005.md) | Ver acciones acordadas con responsables | P1 |
| [US-006](./user-stories/US-006.md) | Ver minuta formal | P1 |
| [US-007](./user-stories/US-007.md) | Ver resumen ejecutivo | P1 |
| [US-008](./user-stories/US-008.md) | Subir archivos desde la interfaz web | P2 |
| [US-009](./user-stories/US-009.md) | Consultar historial de reuniones | P2 |
| [US-010](./user-stories/US-010.md) | Procesar reuniones vía API REST | P2 |
| [US-011](./user-stories/US-011.md) | Recibir feedback ante errores | P2 |
| [US-012](./user-stories/US-012.md) | Almacenar reuniones de forma persistente | P1 |

Cada archivo incluye: metadatos, descripción ampliada, criterios de aceptación, especificación BDD, archivos a modificar, personas vinculadas y notas técnicas.

---

## Resumen por User Story

| ID | Resumen (Como... Quiero... Para...) |
|----|-------------------------------------|
| US-000 | Como Pablo/Tech Lead, quiero estructura + Hello World E2E para validar el setup |
| US-001 | Como Marina/Pablo, quiero subir grabación (audio/video) para obtener documentación sin transcribir |
| US-002 | Como Marina/Pablo, quiero subir notas en TXT/MD para obtener documentación sin transcripción |
| US-003 | Como Ricardo, quiero ver participantes identificados para asignar responsabilidades |
| US-004 | Como Elena/Ricardo, quiero ver temas principales para entender el alcance sin revisar todo |
| US-005 | Como Ricardo/Pablo, quiero ver acciones con responsables para seguimiento y trazabilidad |
| US-006 | Como Marina/Ricardo, quiero minuta formal para compartir documentación profesional |
| US-007 | Como Elena, quiero resumen ejecutivo ultra-conciso para captar puntos clave en segundos |
| US-008 | Como Marina/Pablo, quiero interfaz web para subir archivos sin usar CLI ni API |
| US-009 | Como Ricardo/Elena, quiero historial de reuniones para acceder a documentación pasada |
| US-010 | Como Pablo/integrador, quiero API REST para integrar MeetMind con otros sistemas |
| US-011 | Como Marina/usuario, quiero mensajes claros ante errores para entender qué hacer |
| US-012 | Como sistema, quiero persistir reuniones en BD para consulta posterior y trazabilidad |

---

## Referencias

- [README del directorio user-stories](./user-stories/README.md) — Índice completo con orden de implementación y dependencias
- [PRD del proyecto](../PRD-Sistema-Procesamiento-Reuniones-IA.md)
- [Backlog priorizado](./03-backlog-priorizado.md)
