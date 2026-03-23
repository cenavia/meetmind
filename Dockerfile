# MeetMind - Hugging Face Spaces (API FastAPI + UI Gradio)
# Puerto expuesto: 7860 (Gradio). API interna: 8000
#
# Optimización multimedia (Whisper local en CPU):
# - Precarga del modelo en build (evita descarga ~461 MB en el primer request).
# - OMP_NUM_THREADS = nproc en entrypoint (usa todos los cores del contenedor).
# - Build más rápido en CPU: docker build --build-arg WHISPER_DOCKER_MODEL=base .

FROM python:3.11-slim AS builder

WORKDIR /build

# Dependencias del sistema para compilación (opcional, acelera algunos wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md uv.lock* ./
COPY src ./src

# Instalar paquete en entorno virtual
RUN pip install --no-cache-dir uv \
    && uv venv /opt/venv \
    && . /opt/venv/bin/activate && uv pip install .

# Precargar pesos Whisper (mismo nombre que TRANSCRIPTION_MODEL por defecto en runtime)
ARG WHISPER_DOCKER_MODEL=small
ENV XDG_CACHE_HOME=/opt/whisper-model-cache
RUN mkdir -p /opt/whisper-model-cache \
    && . /opt/venv/bin/activate \
    && python -c "import whisper; whisper.load_model(\"${WHISPER_DOCKER_MODEL}\", device=\"cpu\")"

# ---
FROM python:3.11-slim AS runtime

# ffmpeg para Whisper (decodificación de audio/vídeo)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY docker/entrypoint.sh /usr/local/bin/meetmind-entrypoint.sh
RUN chmod +x /usr/local/bin/meetmind-entrypoint.sh

# Usuario requerido por HF Spaces (UID 1000)
RUN useradd -m -u 1000 user

ARG WHISPER_DOCKER_MODEL=small
ENV HOME=/home/user \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    API_BASE_URL=http://localhost:8000 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    TRANSCRIPTION_MODEL=${WHISPER_DOCKER_MODEL}

WORKDIR /home/user/app

# Copiar venv desde builder
COPY --from=builder /opt/venv /opt/venv

# Pesos Whisper precargados → ~/.cache/whisper del usuario de la app
COPY --from=builder /opt/whisper-model-cache/whisper /home/user/.cache/whisper

# Copiar código
COPY --chown=user:user . .

# Permitir escritura de SQLite y otros datos en el directorio de trabajo
# (evita "unable to open database file" cuando DATABASE_URL=sqlite:///./meetmind.db)
RUN chown -R user:user /home/user/app /home/user/.cache

# Fallback para Docker: si .env no define DATABASE_URL, usar /tmp (siempre escribible)
ENV DATABASE_URL=sqlite:////tmp/meetmind.db

USER user

EXPOSE 7860

ENTRYPOINT ["/usr/local/bin/meetmind-entrypoint.sh"]
# API en background (8000), Gradio en foreground (7860)
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & sleep 3 && exec python -m src.ui.app"]
