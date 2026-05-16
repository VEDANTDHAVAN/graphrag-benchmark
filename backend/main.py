import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from backend.routes import ingestion, metrics, query
from backend.routes.graph import router as graph_router
from backend.security import (
    path_writable,
    production_config_errors,
    rate_limit_middleware,
    request_size_middleware,
)
from utils.paths import chroma_path, graph_path, upload_dir

app = FastAPI(title="GraphRAG Benchmark API")

frontend_url = os.getenv("FRONTEND_URL", "").strip()
cors_origins_env = os.getenv("CORS_ORIGINS", frontend_url).strip()
cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
allow_origin_regex = os.getenv("CORS_ORIGIN_REGEX")  # optional

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["http://localhost:3000", "http://localhost:3005"],
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(request_size_middleware)

app.include_router(ingestion.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(graph_router)


@app.on_event("startup")
def validate_startup_config():
    errors = production_config_errors()
    if errors:
        raise RuntimeError("; ".join(errors))


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/ready")
def ready_check():
    graph_file = Path(graph_path())
    checks = {
        "production_config": production_config_errors(),
        "chroma_path_writable": path_writable(chroma_path()),
        "upload_dir_writable": path_writable(upload_dir()),
        "graph_artifact_present": graph_file.exists(),
        "tigergraph_enabled": os.getenv("TIGERGRAPH_ENABLED", "false").lower() == "true",
        "networkx_primary": True,
    }
    if checks["tigergraph_enabled"]:
        checks["tigergraph_configured"] = all(
            os.getenv(key)
            for key in (
                "TIGERGRAPH_HOST",
                "TIGERGRAPH_GRAPH",
                "TIGERGRAPH_USERNAME",
                "TIGERGRAPH_PASSWORD",
            )
        )
    else:
        checks["tigergraph_configured"] = "skipped"

    ready = (
        not checks["production_config"]
        and checks["chroma_path_writable"]
        and checks["upload_dir_writable"]
        and (checks["tigergraph_configured"] is True or checks["tigergraph_configured"] == "skipped")
    )
    return {"status": "ready" if ready else "not_ready", "checks": checks}
