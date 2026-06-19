# Multi-stage Dockerfile per il Bot Telegram
# Stage 1: Build dependencies
FROM python:3.11-slim as builder

# Variabili d'ambiente per build
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Installa dipendenze di sistema per build
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crea ambiente virtuale
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e installa dipendenze Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Metadata
LABEL maintainer="telegram-bot"
LABEL description="Bot Telegram Personalizzato"
LABEL version="1.0.0"

# Variabili d'ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Installa solo le dipendenze runtime necessarie
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crea utente non-root per sicurezza
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Copia ambiente virtuale dal builder
COPY --from=builder /opt/venv /opt/venv

# Directory di lavoro
WORKDIR /app

# Copia il codice dell'applicazione con struttura ottimizzata
COPY --chown=botuser:botuser src/ ./src/
COPY --chown=botuser:botuser *.py ./
COPY --chown=botuser:botuser *.md ./

# Crea directory per logs e data
RUN mkdir -p /app/logs /app/data && \
    chown -R botuser:botuser /app

# Cambia all'utente non-root
USER botuser

# Health check ottimizzato
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Espone porta per health check
EXPOSE 8000

# Comando di avvio (usa la versione cloud per produzione)
CMD ["python", "src/bot/main_cloud.py"]
