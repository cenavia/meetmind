"""Prompts para identificación de temas principales."""

IDENTIFY_TOPICS_PROMPT = """Eres un asistente que identifica los temas principales discutidos en una reunión a partir del texto de transcripción o notas.

INSTRUCCIONES:
- Extrae entre 1 y 5 temas principales discutidos en el texto.
- Cada tema debe tener granularidad apropiada: ni muy general (evitar "Reunión de trabajo", "Discusión general", "Reunión") ni demasiado específico.
- NO inventes temas: si hay menos de 3 temas identificables, devuelve solo los que existan. Nunca rellenes con temas ficticios.
- Si hay temas solapados (ej. "Presupuesto" y "Presupuesto Q2"), consolida en UN solo tema prefiriendo la variante más específica (ej. "Presupuesto Q2").
- Ordena los temas por su primera aparición en el texto.
- Si no hay temas identificables en el texto, devuelve una lista vacía.
- Los temas deben ser concretos y derivables del contenido (ej. "Sprint 12", "Módulo de facturación", "Presupuesto Q2").

TEXTO DE LA REUNIÓN:
{raw_text}

Devuelve la lista de temas principales (1-5 elementos, sin genéricos, consolidados si solapados, orden por primera aparición). Si no hay temas claros, lista vacía.
"""
