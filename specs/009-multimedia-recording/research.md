# Research: Procesar grabación multimedia

**Feature**: 009-multimedia-recording | **Date**: 2026-03-22

## Resumen

No se identificaron NEEDS CLARIFICATION en el Technical Context. Las decisiones técnicas se derivan de la spec clarificada, la Constitución, el stack existente (FastAPI, LangGraph) y las restricciones de la spec (500 MB, 15 min timeout, mensajes español, flujo híbrido sync/async). Este documento consolida las elecciones de diseño.

---

## 1. Servicio de transcripción (Speech-to-Text)

**Decisión**: Usar `openai-whisper` (Whisper local) como proveedor de transcripción por defecto. Modelo `base` o `small` para equilibrio velocidad/calidad. Configurable vía variable de entorno `TRANSCRIPTION_MODEL` (tiny, base, small, medium, large).

**Rationale**: Whisper local evita coste de API externa, funciona offline, soporta múltiples idiomas con detección automática. La Constitución indica "proveedor de transcripción" configurable; Whisper cumple. Requiere ffmpeg (estándar para multimedia). Alternativa cloud: OpenAI Speech-to-Text API — mayor coste, requiere API key; útil para despliegues sin ffmpeg.

**Alternativas consideradas**:
- OpenAI Speech-to-Text API: pago por minuto; requiere red; mejor para SaaS escalable.
- AssemblyAI / Deepgram: terceros; más integración.
- Vosk: más ligero pero menor calidad; Whisper es referencia en precisión.

---

## 2. Extracción de audio desde video

**Decisión**: Usar ffmpeg vía subprocess o pydub. ffmpeg está en las dependencias de Whisper para manejar contenedores. Para video (MP4, MOV, WEBM, MKV), extraer pista de audio a WAV temporal antes de transcribir. pydub abstrae ffmpeg; alternativamente, subprocess directo a ffmpeg.

**Rationale**: Whisper acepta archivos de audio; para video hay que extraer el canal de audio. ffmpeg es estándar y Whisper ya lo requiere. pydub simplifica la API (AudioSegment.from_file); si se evita dependencia extra, subprocess a ffmpeg con `-vn -acodec pcm_s16le` es suficiente.

**Alternativas consideradas**:
- moviepy: más pesado; orientado a edición de video.
- ffmpeg-python: wrapper Python; pydub es más simple para este caso.

---

## 3. Codecs soportados

**Decisión**: Whisper y ffmpeg soportan H.264, AAC, MP3, PCM, VP8/VP9 (WEBM), etc. No validar codec explícitamente; intentar transcripción y, si ffmpeg/Whisper fallan, capturar excepción y devolver mensaje amigable "El formato del archivo no es compatible" (español), sin exponer detalles técnicos. Alineado con FR-008 y clarificación de rechazo por codec.

**Rationale**: Validar todos los codecs posibles es complejo y frágil. Delegar en ffmpeg/Whisper; el fallo natural se traduce a mensaje de usuario.

---

## 4. Ubicación de la transcripción en el flujo

**Decisión**: Realizar la transcripción en la capa API (`process_file`) antes de invocar el grafo. El grafo sigue recibiendo solo `raw_text`. El nodo preprocess no necesita detectar multimedia; la API ya habrá convertido multimedia → texto. Flujo: API recibe archivo → si MIME multimedia, transcribir → raw_text → graph.invoke.

**Rationale**: Mantiene el grafo puro (solo texto); la transcripción es responsabilidad de la capa de entrada. La API orquesta validación, transcripción y invocación del grafo. Menos acoplamiento; preprocess permanece simple.

**Alternativas consideradas**:
- Transcripción en preprocess: el nodo necesitaría acceso a bytes del archivo; el estado actual solo tiene raw_text. Habría que pasar el archivo en el estado, aumentando complejidad.
- Servicio separado: la transcripción ya es un servicio; la orquestación en la API es correcta.

---

## 5. Flujo asíncrono (timeout > 15 min)

**Decisión**: Para MVP, implementar timeout de 15 min en la invocación síncrona. Si la transcripción + workflow superan 15 min, la request falla con timeout. El flujo asíncrono (job ID, consulta posterior) se documenta como requisito pero puede implementarse en una iteración posterior con: almacén de jobs (SQLModel/Redis), endpoint GET /jobs/{job_id}, y worker en background. La spec exige FR-010; para primera entrega se puede usar un diseño simplificado: timeout HTTP 408 con mensaje "El procesamiento tardó demasiado. Intenta con un archivo más corto o vuelve a intentar más tarde." y planear el flujo async completo en una tarea dedicada.

**Rationale**: El flujo async completo (job queue, persistencia, polling) añade complejidad significativa. La spec permite un MVP que cumpla el caso síncrono y gestione el timeout con mensaje claro; el async se puede priorizar según feedback de usuarios. Si se exige async desde el inicio, se necesitaría: asyncio + threading para ejecutar transcripción en background, modelo Job en DB, endpoint de consulta.

**Nota**: Si el producto requiere async desde día 1, la implementación debe incluir: 1) lanzar transcripción en thread/process, 2) devolver job_id inmediatamente con 202 Accepted, 3) almacén de jobs (dict + TTL o DB), 4) GET /jobs/{id} para consultar estado y resultado.

---

## 6. Validación MIME y extensión

**Decisión**: Validar por extensión en la API (MP4, MOV, MP3, WAV, M4A, WEBM, MKV) y, si es posible, por Content-Type/MIME. Mantener alineación con 008: la UI valida antes de enviar; la API re-valida por seguridad. MIME permitidos: audio/mpeg, audio/wav, audio/x-wav, audio/mp4, audio/m4a, video/mp4, video/quicktime, video/webm, video/x-matroska (y variantes). Si Content-Type no coincide con extensión, priorizar extensión para evitar falsos negativos en uploads mal etiquetados.

**Rationale**: FR-005 exige rechazo de formatos no soportados. Doble validación (extensión + MIME) mejora seguridad. Algunos clientes envían application/octet-stream; en ese caso, confiar en la extensión si está en la lista.

---

## 7. Configuración

**Decisión**: Variables de entorno: `TRANSCRIPTION_MODEL` (default: base), `MAX_FILE_SIZE_MB` (default: 500), `PROCESSING_TIMEOUT_SEC` (default: 900 = 15 min). Sin hardcodear credenciales; Whisper local no requiere API key. Si en el futuro se usa OpenAI Speech-to-Text, `OPENAI_API_KEY` ya está en el proyecto.

**Rationale**: Constitución exige configuración vía env para API keys y límites. Valores por defecto alineados con spec clarificada.
