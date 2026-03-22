# Quickstart: Ver temas principales discutidos

**Feature**: 004-identify-topics | **Tiempo estimado**: <5 min (asumiendo 001/002/003 ya ejecutados)

## Prerrequisitos

- Features 001-hello-world-e2e, 002-text-notes-processing y 003-participants-extraction implementadas
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

## 3. Probar extracción de temas

### Con texto con múltiples temas

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión con Juan y María. Se discutió el presupuesto Q2, los plazos del proyecto y la asignación de recursos. Juan propuso revisar las cifras."}'
```

**Resultado esperado** (topics extraídos, 3-5 elementos, separados por punto y coma):

```json
{
  "participants": "Juan, María",
  "topics": "Presupuesto Q2; Plazos del proyecto; Asignación de recursos",
  "actions": "...",
  "minutes": "...",
  "executive_summary": "..."
}
```

### Con texto sin temas identificables

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión de coordinación."}'
```

**Resultado esperado** (topics = "No hay temas identificados"):

```json
{
  "participants": "No identificados",
  "topics": "No hay temas identificados",
  ...
}
```

## 4. Verificar en la UI

1. Ejecutar la UI: `uv run gradio src/ui/app.py`
2. Pegar texto con varios temas o subir archivo .txt/.md
3. Pulsar **Procesar**
4. Verificar que aparece un indicador de carga durante el procesamiento
5. Comprobar que la sección **Temas** muestra la lista extraída (separada por punto y coma) o "No hay temas identificados"
6. En caso de error (API caída, timeout), verificar que el loader se oculta y se muestra mensaje de error

## 5. Referencias

- [Contract: Campo topics](./contracts/topics-field.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
