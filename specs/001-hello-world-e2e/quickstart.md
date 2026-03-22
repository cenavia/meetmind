# Quickstart: Hello World E2E

**Feature**: 001-hello-world-e2e | **Tiempo estimado**: <15 min

## Prerrequisitos

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## 1. Instalación

```bash
cd meetmind
uv sync
```

## 2. Ejecutar la API

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Verificar:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

## 3. Ejecutar la UI

En otra terminal:

```bash
# Opción A: URL por defecto (localhost:8000)
uv run gradio src/ui/app.py

# Opción B: API en otra URL
API_BASE_URL=http://localhost:8000 uv run gradio src/ui/app.py
```

La UI se abre en http://localhost:7860 (por defecto).

## 4. Flujo E2E

1. Escribir texto en el campo de entrada (ej.: "Reunión con Juan y María. Discutimos el presupuesto.")
2. Pulsar **Procesar**
3. Ver el resultado estructurado (participantes, temas, acciones, minuta, resumen)

## 5. Probar la API directamente

```bash
curl -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text": "Reunión de prueba con Juan y María."}'
```

## 6. Ejecutar el grafo en modo standalone (opcional)

```bash
uv run python -c "
from src.agents.meeting.agent import get_graph
g = get_graph()
result = g.invoke({'raw_text': 'Reunión de prueba con Juan y María.'})
print(result)
"
```

## Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| API_BASE_URL | http://localhost:8000 | URL base de la API (solo UI) |
| OPENAI_API_KEY | — | No requerido en Hello World (modo mock) |

## Solución de problemas

- **La UI no conecta con la API**: Comprobar que la API está en marcha y que `API_BASE_URL` apunta al host/puerto correctos.
- **ModuleNotFoundError**: Ejecutar `uv sync` de nuevo.
- **Puerto en uso**: Cambiar `--port` en uvicorn o la configuración de Gradio.
