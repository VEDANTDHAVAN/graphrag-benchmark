from fastapi import APIRouter
from pydantic import BaseModel

from pipelines.graphrag.graphrag_client import TigerGraphClient

router = APIRouter()


class TigerGraphHealth(BaseModel):
    ok: bool
    host: str
    graph: str
    restpp_version_ok: bool = False
    graph_exists: bool = False
    error: str | None = None


@router.get("/tigergraph/health", response_model=TigerGraphHealth)
def tigergraph_health():
    client = TigerGraphClient()

    health = TigerGraphHealth(ok=False, host=client.host, graph=client.graph)

    try:
        # Use RESTPP /version which does not require a graph.
        version = client._get_version()
        health.restpp_version_ok = bool(version) and not version.get("error", False)

        # Check the benchmark graph exists by listing one vertex type with limit=1.
        # If graph does not exist, RESTPP returns an error.
        client._get("/vertices/BenchDocument", params={"limit": 1})
        health.graph_exists = True

        health.ok = health.restpp_version_ok and health.graph_exists
        return health
    except Exception as exc:
        health.error = str(exc)
        return health
