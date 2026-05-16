FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend
COPY evaluation /app/evaluation
COPY ingestion /app/ingestion
COPY pipelines /app/pipelines
COPY scripts /app/scripts
COPY utils /app/utils
COPY data /app/data

ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV CHROMA_PATH=/app/data/chroma
ENV GRAPH_PATH=/app/data/graph/graphrag_graph.pkl
ENV UPLOAD_DIR=/app/data/uploads
ENV TIGERGRAPH_ENABLED=false

EXPOSE 7860

CMD ["sh", "-c", "python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
