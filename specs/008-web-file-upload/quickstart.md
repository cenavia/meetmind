# Quickstart: Subir archivos desde la interfaz web

**Feature**: 008-web-file-upload | **Tiempo estimado**: <5 min (asumiendo API en ejecución)

## Prerrequisitos

- API MeetMind ejecutándose (`uv run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) instalado

## 1. Configuración de la URL de la API (FR-008)

Por defecto la UI usa `http://localhost:8000`. Para usar otra URL:

```bash
export API_BASE_URL=http://localhost:8000
```

Ejemplo para API remota: `export API_BASE_URL=https://api.meetmind.example.com`

## 2. Ejecutar la UI

```bash
cd meetmind
uv sync
uv run gradio src/ui/app.py
```

## 3. Probar la subida de archivos

### Con archivo TXT o MD

1. En la UI, en "O sube un archivo", selecciona un `.txt` o `.md` con notas de reunión
2. El botón **Procesar** se habilita
3. Pulsa **Procesar**
4. Verifica: indicador de progreso durante el procesamiento
5. Resultados en secciones: Participantes, Temas, Acciones, Minuta, Resumen ejecutivo
6. El botón **Procesar** queda desactivado hasta que pulses **Limpiar**

### Con archivo no soportado

1. Intenta subir un `.exe` o `.zip`
2. La UI restringe los formatos en el selector; si se fuerza, al procesar debe mostrar mensaje de error con formatos permitidos

### Con archivo >500 MB

1. Intenta subir un archivo mayor a 500 MB
2. Debe mostrarse: "El archivo supera el límite de 500 MB."

### Con timeout (10 minutos)

1. Si el procesamiento tarda más de 10 minutos, debe mostrarse un mensaje amigable de timeout

## 4. Formatos soportados

| Categoría | Extensiones |
|-----------|-------------|
| Multimedia | MP4, MOV, MP3, WAV, M4A |
| Texto | TXT, MD |

**Nota**: La API actual puede soportar solo TXT/MD. Los formatos multimedia estarán disponibles cuando la API (US-010) los implemente. La UI ya valida y acepta todos los formatos; si la API rechaza uno, se mostrará el mensaje de error correspondiente.

## 5. Referencias

- [Contract: Validación de archivos](./contracts/file-validation.md)
- [Contract: Integración con API](./contracts/api-integration.md)
- [Data Model](./data-model.md)
- [spec.md](./spec.md)
