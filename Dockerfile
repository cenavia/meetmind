# MeetMind - Hugging Face Spaces (API FastAPI + UI Gradio)
# Puerto expuesto: 7860 (Gradio). API interna: 8000

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

# ---
FROM python:3.11-slim AS runtime

# Usuario requerido por HF Spaces (UID 1000)
RUN useradd -m -u 1000 user

ENV HOME=/home/user \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    API_BASE_URL=http://localhost:8000 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

WORKDIR /home/user/app

# Copiar venv desde builder
COPY --from=builder /opt/venv /opt/venv

# Copiar código
COPY --chown=user:user . .

USER user

EXPOSE 7860

# API en background (8000), Gradio en foreground (7860)
CMD uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & \
    sleep 3 && \
    exec python -m src.ui.app
