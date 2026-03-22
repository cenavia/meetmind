# Quickstart: Ver acciones acordadas con responsables

**Feature**: 005-extract-actions | **Tiempo estimado**: <5 min (asumiendo 001-004 ya ejecutados)

## Prerrequisitos

- Features 001-hello-world-e2e, 002-text-notes-processing, 003-participants-extraction y 004-identify-topics implementadas
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

## 3. Probar extracción de acciones

### Con acciones explícitas y responsables

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión con Juan y María. María enviará el informe antes del viernes. Se debe revisar el contrato. Juan se encargará de la presentación."}'
```

**Resultado esperado** (actions en formato acción | responsable; pares separados por punto y coma):

```json
{
  "participants": "Juan, María",
  "topics": "...",
  "actions": "Enviar informe antes del viernes | María; Revisar el contrato | Por asignar; Preparar presentación | Juan",
  "minutes": "...",
  "executive_summary": "..."
}
```

### Con acción sin responsable

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Se acordó revisar el presupuesto la próxima semana."}'
```

**Resultado esperado** (actions con "Por asignar"):

```json
{
  "participants": "No identificados",
  "topics": "...",
  "actions": "Revisar presupuesto la próxima semana | Por asignar",
  ...
}
```

### Sin acciones identificables

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión de brainstorming. Se discutieron ideas sin acuerdos concretos."}'
```

**Resultado esperado** (actions = "No hay acciones identificadas"):

```json
{
  "participants": "No identificados",
  "topics": "...",
  "actions": "No hay acciones identificadas",
  ...
}
```

## 4. Verificar en la UI

1. Ejecutar la UI: `uv run gradio src/ui/app.py`
2. Pegar texto con compromisos o acuerdos (ej. "María enviará el informe; se debe revisar el contrato")
3. Pulsar **Procesar**
4. Comprobar que la sección **Acciones** muestra pares "acción | responsable" separados por punto y coma, o "No hay acciones identificadas" si no hay compromisos

## 5. Referencias

- [Contract: Campo actions](./contracts/actions-field.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
