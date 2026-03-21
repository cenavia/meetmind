El skill se activa con frases relacionadas a su descripción. Según el SKILL.md:

**Prompts de activación:**

| Tipo | Ejemplos |
|------|----------|
| **PRD** | "Analiza este PRD", "Revisa mi PRD", "Tengo un PRD para el proyecto" |
| **User Stories** | "Genera user stories", "Crea historias de usuario", "Necesito user stories del PRD" |
| **Épicas** | "Crea una épica", "Necesito crear un epic para...", "Genera épica de..." |
| **Backlog** | "Prioriza el backlog", "Ordena las historias por prioridad" |
| **Tickets** | "Genera tickets técnicos", "Crea tickets de Jira", "Necesito tickets de trabajo" |
| **BDD** | "Genera especificaciones BDD", "Crea escenarios Gherkin" |
| **Roles** | "Actúa como Product Owner", "Como Business Analyst, analiza..." |

**Ejemplo de prompt inicial:**

```
Tengo el siguiente PRD para mi proyecto:

[pegar PRD aquí]

Genera los user personas, user stories y prioriza el backlog.
```

**Nota:** El skill siempre pedirá el PRD si no lo proporcionas, ya que es obligatorio según la configuración.