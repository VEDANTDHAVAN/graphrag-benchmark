import os
import pickle
from collections import deque
from typing import Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx

from utils.paths import graph_path as get_graph_path


def load_graph(path: Optional[str] = None) -> nx.MultiDiGraph:
    graph_file = path or get_graph_path()
    if not os.path.exists(graph_file):
        return nx.MultiDiGraph()
    with open(graph_file, "rb") as f:
        graph = pickle.load(f)
    return graph if graph is not None else nx.MultiDiGraph()


def find_chunk_node(graph: nx.MultiDiGraph, chunk_id: str) -> Optional[str]:
    if not graph or not chunk_id:
        return None

    direct = f"chunk:{chunk_id}"
    if graph.has_node(direct):
        return direct

    for node_id, data in graph.nodes(data=True):
        if data.get("kind") == "chunk" and data.get("chunk_id") == chunk_id:
            return node_id
    return None


def _chunk_record(graph: nx.MultiDiGraph, node_id: str, distance: int) -> Optional[Dict]:
    if not graph.has_node(node_id):
        return None
    data = graph.nodes[node_id]
    if data.get("kind") != "chunk":
        return None
    return {
        "chunk_id": data.get("chunk_id"),
        "doc_id": data.get("doc_id"),
        "text": data.get("text", ""),
        "source": "graph_expansion",
        "graph_distance": distance,
        "node_id": node_id,
    }


def get_neighbor_chunks(graph: nx.MultiDiGraph, node_id: str, hops: int = 1) -> List[Dict]:
    if not graph or not node_id or not graph.has_node(node_id):
        return []

    max_depth = max(1, hops) * 2
    queue = deque([(node_id, 0)])
    visited: Set[str] = {node_id}
    chunks: List[Dict] = []
    seen_chunks: Set[str] = set()

    while queue:
        current, distance = queue.popleft()
        if distance >= max_depth:
            continue

        neighbors = set()
        if hasattr(graph, "successors"):
            neighbors.update(graph.successors(current))
        if hasattr(graph, "predecessors"):
            neighbors.update(graph.predecessors(current))

        for neighbor in neighbors:
            if neighbor in visited:
                continue
            visited.add(neighbor)
            next_distance = distance + 1
            record = _chunk_record(graph, neighbor, next_distance)
            if record:
                key = record.get("chunk_id") or record.get("text", "")
                if key and key not in seen_chunks:
                    chunks.append(record)
                    seen_chunks.add(key)
            queue.append((neighbor, next_distance))

    return chunks


def get_connected_entities(graph: nx.MultiDiGraph, chunk_id: str) -> List[Dict]:
    chunk_node = find_chunk_node(graph, chunk_id)
    if not chunk_node:
        return []

    entities: List[Dict] = []
    seen: Set[str] = set()
    neighbors = set(graph.successors(chunk_node)) | set(graph.predecessors(chunk_node))
    for node_id in neighbors:
        data = graph.nodes.get(node_id, {})
        if data.get("kind") != "entity":
            continue
        entity_id = data.get("entity_id") or data.get("label") or node_id
        if entity_id in seen:
            continue
        seen.add(entity_id)
        entities.append(
            {
                "node_id": node_id,
                "entity_id": entity_id,
                "label": data.get("label") or entity_id,
                "name": data.get("name") or entity_id,
                "entity_type": data.get("entity_type"),
            }
        )
    return entities


def collect_subgraph_trace(
    graph: nx.MultiDiGraph,
    seed_nodes: Iterable[str],
    expanded_nodes: Iterable[str],
) -> Dict:
    nodes = [n for n in dict.fromkeys([*seed_nodes, *expanded_nodes]) if graph.has_node(n)]
    node_set = set(nodes)
    edges: List[Dict] = []

    for u, v, key, data in graph.edges(keys=True, data=True):
        if u not in node_set and v not in node_set:
            continue
        edges.append(
            {
                "source": u,
                "target": v,
                "key": key,
                "kind": data.get("kind"),
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
    }
