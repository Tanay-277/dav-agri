FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Edge TTS and gTTS require a CA bundle for outbound HTTPS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create the SQLite data directory up front. Docker seeds a fresh named volume
# from this directory, which also carries its ownership across - without this the
# volume is created root-owned and the unprivileged user cannot open the database.
RUN mkdir -p /data

# Runs unprivileged.
RUN useradd --create-home --uid 1000 dav && chown -R dav:dav /app /data
USER dav

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]