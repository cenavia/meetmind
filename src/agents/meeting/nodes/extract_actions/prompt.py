"""Prompts para extracción de acciones acordadas con responsables."""

EXTRACT_ACTIONS_PROMPT = """Eres un asistente que extrae las acciones acordadas en una reunión a partir del texto de transcripción o notas.

INSTRUCCIONES:
- Extrae cada acción acordada con su responsable asignado.
- Formato de cada par: acción (descripción breve) y responsable (nombre propio o "Por asignar").
- Variantes lingüísticas de compromiso: "se encargará", "debe", "comprometió a", "acordó que", "enviará", etc.
- Responsable SOLO por nombre propio explícito. Si el responsable se menciona solo por cargo (ej. "el gerente"), usa "Por asignar".
- Si una acción tiene varios responsables explícitos (ej. "María y Pedro se encargarán"), usa el PRIMER nombre mencionado.
- Sin responsable identificable → siempre "Por asignar". NUNCA inventes un responsable.
- Acciones redundantes (misma acción con distintas redacciones) → consolidar en UNA, preferir la variante más específica (ej. con plazo o detalle).
- NO incluyas los caracteres "|" ni ";" dentro de acción ni responsable; reformula para evitarlos.
- Incluye acciones implícitas cuando sean razonablemente inferibles del contexto; NO inventes acciones sin evidencia textual.
- Si no hay acciones ni acuerdos identificables, devuelve una lista vacía.
- NO inventes acciones. Si solo hay discusiones sin acuerdos concretos, lista vacía.

TEXTO DE LA REUNIÓN:
{raw_text}

Devuelve la lista de pares acción-responsable. Cada item tiene "action" (descripción breve de la acción) y "responsible" (nombre o "Por asignar"). Si no hay acciones, lista vacía.
"""
