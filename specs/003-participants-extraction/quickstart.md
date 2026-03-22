# Quickstart: Ver extracción de participantes

**Feature**: 003-participants-extraction | **Tiempo estimado**: <5 min (asumiendo 001/002 ya ejecutados)

## Prerrequisitos

- Features 001-hello-world-e2e y 002-text-notes-processing implementadas
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

## 3. Probar extracción de participantes

### Con texto que incluye nombres

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión con Juan Pérez, María López y Pedro García. Juan propuso revisar el presupuesto. María acordó enviar la propuesta."}'
```

**Resultado esperado** (participants extraídos, deduplicados, orden por primera aparición):

```json
{
  "participants": "Juan Pérez, María López, Pedro García",
  "topics": "...",
  "actions": "...",
  "minutes": "...",
  "executive_summary": "..."
}
```

### Con texto sin nombres

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Se discutió el presupuesto. Hubo acuerdo sobre las fechas."}'
```

**Resultado esperado** (participants = "No identificados"):

```json
{
  "participants": "No identificados",
  ...
}
```

## 4. Verificar en la UI

1. Ejecutar la UI: `uv run gradio src/ui/app.py`
2. Pegar texto con nombres de participantes o subir archivo .txt/.md
3. Pulsar **Procesar**
4. Comprobar que la sección **Participantes** muestra la lista extraída o "No identificados"

## 5. Referencias

- [Contract: Campo participants](./contracts/participants-field.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
