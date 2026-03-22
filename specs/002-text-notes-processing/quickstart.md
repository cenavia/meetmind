# Quickstart: Procesar notas en texto (archivos TXT/MD)

**Feature**: 002-text-notes-processing | **Tiempo estimado**: <10 min (asumiendo 001 ya ejecutado)

## Prerrequisitos

- Feature 001-hello-world-e2e implementada y funcional
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado

## 1. Instalación

```bash
cd meetmind
uv sync
```

## 2. Ejecutar la API

```bash
uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Ejecutar la UI

En otra terminal:

```bash
uv run gradio src/ui/app.py
```

La UI se abre en http://localhost:7860. Ahora incluye:
- **Área de texto**: pegar notas directamente (modo existente)
- **Selector de archivo**: arrastrar o seleccionar .txt o .md

Solo una opción activa a la vez; si hay texto, el archivo está bloqueado y viceversa.

## 4. Flujo E2E con archivo

1. **Subir archivo**: Arrastrar un .txt o .md al área de archivos, o pulsar para seleccionar
2. **Procesar**: Pulsar **Procesar** → barra de progreso durante subida, luego "Procesando..."
3. **Resultado**: Ver participantes, temas, acciones, minuta y resumen estructurados

## 5. Probar la API de archivos directamente

Crear un archivo de prueba:

```bash
echo "Reunión con Juan y María. Discutimos el presupuesto y las fechas." > /tmp/notas.txt
```

Enviar a la API:

```bash
curl -X POST http://localhost:8000/api/v1/process/file \
  -F "file=@/tmp/notas.txt"
```

Respuesta esperada (mismo esquema que /process/text):

```json
{
  "participants": "...",
  "topics": "...",
  "actions": "...",
  "minutes": "...",
  "executive_summary": "..."
}
```

## 6. Casos de error

| Caso | Resultado |
|------|-----------|
| Archivo PDF o DOCX | 400: "Solo se admiten archivos .txt y .md" |
| Archivo vacío | 422: "El archivo está vacío o contiene solo espacios" |
| Contenido >50.000 caracteres | 400: "El contenido excede el límite de 50000 caracteres" |

## Referencias

- [API Contract: POST /api/v1/process/file](./contracts/api-process-file.md)
- [COMO-EJECUTAR.md](../../docs/planning/COMO-EJECUTAR.md) (documentación principal)
