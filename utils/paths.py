import os
from pathlib import Path


def repo_root() -> Path:
    # utils/paths.py -> repo root is parent of utils/
    return Path(__file__).resolve().parents[1]


def _resolve_env_path(env_key: str, default_relative: str) -> str:
    """
    Resolve a runtime path from environment, falling back to a repo-relative default.

    - If env var is set, it can be absolute or relative (relative -> relative to repo root).
    - If not set, use default_relative under repo root.
    """
    val = os.getenv(env_key)
    if val:
        p = Path(val)
        if p.is_absolute():
            return str(p)
        return str(repo_root() / p)
    return str(repo_root() / default_relative)


def chroma_path() -> str:
    # Render disk mount suggestion: /data/chroma
    return _resolve_env_path("CHROMA_PATH", "data/chroma")


def graph_path() -> str:
    # Render disk mount suggestion: /data/graph/graphrag_graph.pkl
    return _resolve_env_path("GRAPH_PATH", "data/graph/graphrag_graph.pkl")


def upload_dir() -> str:
    # Render disk mount suggestion: /data/uploads
    return _resolve_env_path("UPLOAD_DIR", "data/uploads")

