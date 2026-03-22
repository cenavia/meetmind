# Contract: Validación de archivos en la UI

**Feature**: 008-web-file-upload | **Aplica a**: Componente de upload (`gr.File`), función de procesamiento

---

## Formatos permitidos

| Categoría | Extensiones |
|-----------|-------------|
| Multimedia | .mp4, .mov, .mp3, .wav, .m4a |
| Texto | .txt, .md |

Validación: case-insensitive. Ejemplo: `.MP4` válido.

---

## Tamaño máximo

- **Límite**: 500 MB (500 * 1024 * 1024 bytes)
- **Validación**: Antes de enviar a la API; si excede, no enviar y mostrar mensaje.

---

## Mensajes de error (español)

| Condición | Mensaje |
|-----------|---------|
| Formato no soportado | "Formato no soportado. Formatos permitidos: multimedia (MP4, MOV, MP3, WAV, M4A), texto (TXT, MD)." |
| Archivo > 500 MB | "El archivo supera el límite de 500 MB." |
| Sin archivo al procesar | "Selecciona un archivo antes de procesar." |

---

## Orden de validación

1. ¿Hay archivo seleccionado?
2. ¿Extensión permitida?
3. ¿Tamaño ≤ 500 MB?
4. Si todo OK → enviar a la API.
