# Quickstart: Ver minuta formal

**Feature**: 006-generate-minutes | **Tiempo estimado**: <5 min (asumiendo 001-005 ya ejecutados)

## Prerrequisitos

- Features 001-hello-world-e2e, 002-text-notes-processing, 003-participants-extraction, 004-identify-topics y 005-extract-actions implementadas
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

## 3. Probar generación de minuta

### Con información completa

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión con Juan y María. Se discutió el presupuesto trimestral. María enviará el informe antes del viernes. Juan preparará la presentación."}'
```

**Resultado esperado** (minutes: minuta narrativa ≤150 palabras, en español):

```json
{
  "participants": "Juan, María",
  "topics": "...",
  "actions": "...",
  "minutes": "Reunión con Juan y María. Se discutió el presupuesto trimestral...",
  "executive_summary": "..."
}
```

### Con información parcial (solo temas)

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión de brainstorming. Se habló de ideas, innovación y presupuesto. Sin acuerdos concretos."}'
```

**Resultado esperado** (minutes integra lo disponible):

```json
{
  "participants": "No identificados",
  "topics": "...",
  "actions": "No hay acciones identificadas",
  "minutes": "Reunión de brainstorming. Temas abordados: ideas, innovación y presupuesto...",
  "executive_summary": "..."
}
```

### Sin datos procesables

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "..."}'
```

**Resultado esperado** (minutes = mensaje fijo):

```json
{
  "participants": "No identificados",
  "topics": "No hay temas identificados",
  "actions": "No hay acciones identificadas",
  "minutes": "Minuta: No se identificó información procesable en la reunión.",
  "executive_summary": "..."
}
```

## 4. Verificar en la UI

1. Ejecutar la UI: `uv run gradio src/ui/app.py`
2. Pegar texto con participantes, temas y/o acciones
3. Pulsar **Procesar**
4. Comprobar que la sección **Minuta** muestra texto narrativo formal ≤150 palabras, o el mensaje fijo si no hay datos

## 5. Referencias

- [Contract: Campo minutes](./contracts/minutes-field.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
