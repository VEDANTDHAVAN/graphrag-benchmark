from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.routes import ingestion, query

app = FastAPI(title="GraphRAG Benchmark API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router, prefix="/api")
app.include_router(query.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
