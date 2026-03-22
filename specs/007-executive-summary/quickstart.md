# Quickstart: Ver resumen ejecutivo

**Feature**: 007-executive-summary | **Tiempo estimado**: <5 min (asumiendo 001-006 ya ejecutados)

## Prerrequisitos

- Features 001 a 006 implementadas
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado
- Variable `OPENAI_API_KEY` configurada (o proveedor LLM alternativo)

## 1. Instalación

```bash
cd meetmind
uv sync
```

## 2. Ejecutar la API

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Probar generación de resumen ejecutivo

### Con información completa

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión con Juan y María. Se discutió el presupuesto trimestral. María enviará el informe antes del viernes. Juan preparará la presentación."}'
```

**Resultado esperado** (executive_summary: ≤30 palabras, español):

```json
{
  "participants": "Juan, María",
  "topics": "...",
  "actions": "...",
  "minutes": "...",
  "executive_summary": "Acuerdo sobre presupuesto. María envía informe; Juan prepara presentación."
}
```

### Sin datos procesables

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'
```

**Resultado esperado** (executive_summary = mensaje fijo):

```json
{
  "participants": "No identificados",
  "topics": "No hay temas identificados",
  "actions": "No hay acciones identificadas",
  "minutes": "Minuta: No se identificó información procesable en la reunión.",
  "executive_summary": "Resumen: No se identificó información procesable en la reunión."
}
```

## 4. Verificar en la UI

1. Ejecutar la UI: `uv run gradio src/ui/app.py`
2. Pegar texto con participantes, temas y/o acciones
3. Pulsar **Procesar**
4. **Verificar**: El botón Procesar se desactiva **inmediatamente** al hacer clic y permanece desactivado durante y después del procesamiento
5. Comprobar que la sección **Resumen ejecutivo** muestra texto ≤30 palabras, o el mensaje fijo si no hay datos
6. Pulsar **Limpiar** → campos se vacían
7. Introducir de nuevo texto o cargar archivo → el botón **Procesar** vuelve a activarse

## 5. Referencias

- [Contract: Campo executive_summary](./contracts/summary-field.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
