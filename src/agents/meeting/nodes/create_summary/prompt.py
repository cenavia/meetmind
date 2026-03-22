"""Prompts para generación de resumen ejecutivo."""

CREATE_SUMMARY_PROMPT = """Eres un asistente que genera resúmenes ejecutivos ultra-concisos de reuniones.

INSTRUCCIONES:
- Genera un RESUMEN EJECUTIVO en español de MÁXIMO 30 palabras.
- Enfócate en: decisiones tomadas, acciones críticas, conclusiones principales.
- Síntesis clara y accionable que permita decidir si leer la minuta completa.
- Para reuniones informativas (sin decisiones explícitas): sintetiza los temas principales con tono profesional.
- NO inventes información que no esté en la entrada.
- Si algún campo indica "No identificados", "No hay temas identificados" o "No hay acciones identificadas", omítelo o intégralo con coherencia.
- Tono profesional. Siempre en español.
- Cuenta las palabras: máximo 30 (split por espacios).

INFORMACIÓN DISPONIBLE:
Participantes: {participants}
Temas: {topics}
Acciones: {actions}
Minuta: {minutes}

Genera el resumen ejecutivo en una o dos frases cortas. Máximo 30 palabras.
"""

SHORTEN_PROMPT = """Acorta el siguiente texto a MÁXIMO 30 palabras en español. Preserva el mensaje clave (decisiones, acciones, conclusiones). Responde solo con el texto acortado, sin explicaciones.

Texto a acortar:
{text}
"""
