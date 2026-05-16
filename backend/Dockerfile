FROM python:3.11-slim

WORKDIR /app

# system deps (small set; keep slim)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code (keep repo structure)
COPY backend /app/backend
COPY ingestion /app/ingestion
COPY evaluation /app/evaluation
COPY pipelines /app/pipelines
COPY utils /app/utils
COPY services /app/services
COPY scripts /app/scripts

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Render sets $PORT; local default remains 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
