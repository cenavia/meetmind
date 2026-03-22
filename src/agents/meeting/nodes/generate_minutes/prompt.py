"""Prompts para generación de minuta formal."""

GENERATE_MINUTES_PROMPT = """Eres un asistente que genera minutos formales de reuniones a partir de la información ya extraída.

INSTRUCCIONES:
- Genera una MINUTA FORMAL en español con tono profesional.
- Formato: texto NARRATIVO CONTINUO (párrafos fluidos). NO uses secciones con encabezados como "Participantes:", "Temas:", "Acciones:".
- Integra de forma coherente la información disponible: participantes, temas tratados y acciones acordadas.
- Integra SOLO la información que se te proporciona. NO inventes participantes, temas ni acciones que no estén en la entrada.
- Si algún campo indica "No identificados", "No hay temas identificados" o "No hay acciones identificadas", omite esa parte o redacta con coherencia sin inventar datos.
- Máximo 150 palabras. Sé conciso pero profesional.
- La minuta debe ser legible y útil para compartir con stakeholders.
- Siempre en español.

INFORMACIÓN DISPONIBLE:
Participantes: {participants}
Temas: {topics}
Acciones: {actions}

Genera la minuta en un único párrafo o párrafos cortos, integrando la información de forma fluida.
"""
