# Quickstart: API REST (012-meetings-rest-api)

**Prerrequisitos**: Python 3.11+, `uv`, variables en `.env` (opcional `DATABASE_URL`), API en marcha.

## Arrancar el servidor

Desde la raíz del repositorio:

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación

- Swagger: http://localhost:8000/docs  
- OpenAPI JSON: http://localhost:8000/openapi.json  

## Sondas

```bash
curl -s http://localhost:8000/health
curl -s -w "\n%{http_code}\n" http://localhost:8000/ready
```

## Procesar texto

```bash
curl -s -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Reunión: Ana y Luis acordaron revisar el presupuesto."}'
```

## Listar y detalle

```bash
curl -s http://localhost:8000/api/v1/meetings
curl -s http://localhost:8000/api/v1/meetings/<UUID>
```

## Procesar archivo (ejemplo)

```bash
curl -s -X POST http://localhost:8000/api/v1/process/file \
  -F "file=@/ruta/al/archivo.txt"
```

El campo multipart del archivo se llama **`file`** (`UploadFile` en `src/api/routers/process.py`).

## CORS

Orígenes permitidos se configuran en `src/api/main.py` (actualmente `*` en desarrollo). Para producción, restringir según despliegue.
