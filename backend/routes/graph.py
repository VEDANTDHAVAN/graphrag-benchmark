from fastapi import APIRouter
import pickle
import os

from utils.paths import graph_path

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/view")
def get_graph_view(limit: int = 200):
    graph_file = graph_path()
    if not os.path.exists(graph_file):
        return {
            "status": "error",
            "message": "Graph file not found",
            "nodes": [],
            "edges": []
        }

    with open(graph_file, "rb") as f:
        graph = pickle.load(f)

    nodes = []
    edges = []

    for node_id, attrs in list(graph.nodes(data=True))[:limit]:
        nodes.append({
            "data": {
                "id": str(node_id),
                "label": attrs.get("label")
                    or attrs.get("name")
                    or attrs.get("title")
                    or attrs.get("text", "")[:40]
                    or str(node_id),
                "type": attrs.get("node_type", attrs.get("type", "unknown"))
            }
        })

    node_ids = set(n["data"]["id"] for n in nodes)

    for source, target, attrs in graph.edges(data=True):
        if str(source) in node_ids and str(target) in node_ids:
            edges.append({
                "data": {
                    "id": f"{source}-{target}",
                    "source": str(source),
                    "target": str(target),
                    "label": attrs.get("relation", attrs.get("type", "RELATED"))
                }
            })

    return {
        "status": "success",
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "total_nodes": graph.number_of_nodes(),
            "total_edges": graph.number_of_edges(),
            "shown_nodes": len(nodes),
            "shown_edges": len(edges)
        }
    }
