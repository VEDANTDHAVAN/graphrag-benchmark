import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.paths import graph_path


def main() -> int:
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    errors = []

    required = ["OPENAI_API_KEY", "FRONTEND_URL", "BACKEND_URL", "ADMIN_API_KEY"]
    if os.getenv("ENV", "").lower() == "production":
        for key in required:
            if not os.getenv(key):
                errors.append(f"Missing required production env var: {key}")
        if not (os.getenv("JWT_SECRET") or os.getenv("SESSION_SECRET")):
            errors.append("Missing JWT_SECRET or SESSION_SECRET")

    health = get_json(f"{backend_url}/health")
    ready = get_json(f"{backend_url}/ready")
    if not health:
        errors.append(f"Backend /health failed at {backend_url}")
    if not ready:
        errors.append(f"Backend /ready failed at {backend_url}")

    graph_file = Path(graph_path())
    if not graph_file.exists():
        errors.append(f"NetworkX graph artifact not found: {graph_file}")

    results_dir = ROOT / "data" / "results"
    try:
        results_dir.mkdir(parents=True, exist_ok=True)
        probe = results_dir / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception as exc:
        errors.append(f"Results directory is not writable: {exc}")

    tigergraph_enabled = os.getenv("TIGERGRAPH_ENABLED", "false").lower() == "true"
    if tigergraph_enabled:
        for key in ("TIGERGRAPH_HOST", "TIGERGRAPH_GRAPH", "TIGERGRAPH_USERNAME", "TIGERGRAPH_PASSWORD"):
            if not os.getenv(key):
                errors.append(f"TigerGraph enabled but {key} is missing")
    else:
        print("TigerGraph validation skipped: TIGERGRAPH_ENABLED=false")

    if health:
        print(f"/health: {health}")
    if ready:
        print(f"/ready: {ready}")

    if errors:
        print("Deployment validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Deployment validation passed.")
    return 0


def get_json(url: str):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError):
        return None


if __name__ == "__main__":
    raise SystemExit(main())
