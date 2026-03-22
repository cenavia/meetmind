"""Prompts para extracción de participantes."""

EXTRACT_PARTICIPANTS_PROMPT = """Eres un asistente que extrae los nombres de las personas que participaron en una reunión a partir del texto de transcripción o notas.

INSTRUCCIONES:
- Extrae ÚNICAMENTE nombres propios de personas que participaron en la reunión.
- NO incluyas términos genéricos como: "persona", "alguien", "un participante", "participante".
- NO incluyas títulos ni honoríficos (Dr., Ing., Sr., Sra., etc.); devuelve solo nombre y apellido.
- Si la misma persona se menciona varias veces (ej. "Juan Pérez" y "Juan"), inclúyela UNA sola vez con la variante más completa disponible (nombre completo preferido).
- Ordena los nombres por su primera aparición en el texto.
- Si no hay nombres identificables en el texto, devuelve una lista vacía.

TEXTO DE LA REUNIÓN:
{raw_text}

Devuelve la lista de participantes (solo nombres, sin títulos, sin duplicados, orden por primera aparición).
"""
