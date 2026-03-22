# Quickstart: persistencia de reuniones (011)

## Prerrequisitos

- Python 3.11+, `uv` o entorno del proyecto instalado (`pyproject.toml`).
- API corriendo como hoy: `uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`.

## Configuración

1. Copiar o editar `.env`:

```bash
# SQLite (por defecto recomendado para dev)
DATABASE_URL=sqlite:///./meetmind.db
```

2. Para PostgreSQL (ejemplo):

```bash
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/meetmind
```

3. Tras implementar la feature: arrancar la API; las tablas deben crearse según la estrategia acordada en el plan (`create_all` en lifespan o script de init).

## Flujo manual de verificación

1. Procesar texto o archivo:

```bash
curl -s -X POST http://localhost:8000/api/v1/process/text \
  -H "Content-Type: application/json" \
  -d '{"text":"Reunión: Ana y Luis acordaron revisar el informe."}'
```

2. Listar reuniones guardadas:

```bash
curl -s http://localhost:8000/api/v1/meetings
```

3. Obtener una por id (sustituir UUID devuelto en listado o en logs si se expone):

```bash
curl -s http://localhost:8000/api/v1/meetings/<UUID>
```

4. Reiniciar la API y repetir el paso 3: los datos deben seguir presentes (SC-001).

## Tests automatizados

```bash
cd /Users/consultor/Documents/projects/meetmind/src && pytest ../tests/unit/db/ ../tests/integration/api/ -q
```

(Ajustar rutas cuando existan los archivos de test de esta feature.)
