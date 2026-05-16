import os
import pickle
import re
import string
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import networkx as nx


from utils.paths import graph_path as get_graph_path


def normalize_text(text: str) -> str:
    """
    Normalization used everywhere:
    - lowercase
    - hyphen -> space
    - remove punctuation
    - collapse spaces
    """
    if not text:
        return ""
    text = text.lower().replace("-", " ")
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _node_id(kind: str, raw_id: str) -> str:
    return f"{kind}:{raw_id}"


@dataclass
class GraphStats:
    graph_loaded: bool
    graph_path: str
    node_count: int
    edge_count: int


class NetworkXGraphClient:
    def __init__(self, graph_path: Optional[str] = None):
        self.graph_path = graph_path or get_graph_path()
        self.graph: nx.MultiDiGraph = nx.MultiDiGraph()

    def load_graph(self) -> nx.MultiDiGraph:
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        if not os.path.exists(self.graph_path):
            self.graph = nx.MultiDiGraph()
            return self.graph
        with open(self.graph_path, "rb") as f:
            self.graph = pickle.load(f)
        return self.graph

    def save_graph(self) -> None:
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        with open(self.graph_path, "wb") as f:
            pickle.dump(self.graph, f)

    def stats(self) -> GraphStats:
        graph_loaded = os.path.exists(self.graph_path)
        node_count = self.graph.number_of_nodes() if self.graph is not None else 0
        edge_count = self.graph.number_of_edges() if self.graph is not None else 0
        return GraphStats(
            graph_loaded=graph_loaded,
            graph_path=self.graph_path,
            node_count=node_count,
            edge_count=edge_count,
        )

    def add_document(self, doc_id: str, title: str, source_file: str) -> str:
        doc_node = _node_id("document", doc_id)
        self.graph.add_node(
            doc_node,
            kind="document",
            doc_id=doc_id,
            title=title,
            source_file=source_file,
            label=title or source_file or doc_id,
        )
        return doc_node

    def add_chunk(self, chunk_id: str, doc_id: str, text: str) -> str:
        chunk_node = _node_id("chunk", chunk_id)
        self.graph.add_node(
            chunk_node,
            kind="chunk",
            chunk_id=chunk_id,
            doc_id=doc_id,
            text=text,
            label=chunk_id,
        )
        doc_node = _node_id("document", doc_id)
        self.graph.add_edge(doc_node, chunk_node, kind="HAS_CHUNK")
        return chunk_node

    def add_entity(self, entity_name: str, entity_type: str = "Concept") -> str:
        entity_id = normalize_text(entity_name)
        ent_node = _node_id("entity", entity_id)
        self.graph.add_node(
            ent_node,
            kind="entity",
            entity_id=entity_id,
            name=entity_name,
            entity_type=entity_type,
            label=entity_id,
        )
        return ent_node

    def add_mentions_edge(self, chunk_id: str, entity_id: str) -> None:
        chunk_node = _node_id("chunk", chunk_id)
        ent_node = _node_id("entity", entity_id)
        self.graph.add_edge(chunk_node, ent_node, kind="MENTIONS", evidence_chunk_id=chunk_id)

    def add_related_edge(
        self,
        entity_a: str,
        entity_b: str,
        evidence_chunk_id: Optional[str] = None,
    ) -> None:
        a = _node_id("entity", entity_a)
        b = _node_id("entity", entity_b)
        attrs: Dict[str, Any] = {"kind": "RELATED_TO"}
        if evidence_chunk_id:
            attrs["evidence_chunk_id"] = evidence_chunk_id
        self.graph.add_edge(a, b, **attrs)
        self.graph.add_edge(b, a, **attrs)

    def search_entities(self, query_entities: Iterable[str]) -> List[str]:
        wanted = [normalize_text(e) for e in query_entities if normalize_text(e)]
        if not wanted:
            return []

        entity_nodes = [
            (n, d)
            for n, d in self.graph.nodes(data=True)
            if d.get("kind") == "entity"
        ]

        matches: List[str] = []
        for normalized in wanted:
            for node, data in entity_nodes:
                label = data.get("label", "")
                if label == normalized:
                    matches.append(data.get("entity_id", normalized))
        # de-dupe preserving order
        seen: Set[str] = set()
        out: List[str] = []
        for m in matches:
            if m not in seen:
                out.append(m)
                seen.add(m)
        return out

    def _chunk_from_node(self, chunk_node: str) -> Optional[Dict[str, Any]]:
        if not self.graph.has_node(chunk_node):
            return None
        data = self.graph.nodes[chunk_node]
        if data.get("kind") != "chunk":
            return None
        return {
            "chunk_id": data.get("chunk_id"),
            "doc_id": data.get("doc_id"),
            "text": data.get("text", ""),
        }

    def get_neighbor_chunks(self, entity_ids: List[str], hops: int = 2, max_chunks: int = 8) -> List[Dict[str, Any]]:
        if not entity_ids:
            return []

        # BFS on entity->entity relations, collecting mentioned chunks at each step.
        frontier = [_node_id("entity", e) for e in entity_ids]
        visited = set(frontier)

        chunks: List[Dict[str, Any]] = []
        chunk_seen: Set[str] = set()

        for _ in range(max(1, hops)):
            next_frontier: List[str] = []
            for ent_node in frontier:
                # chunk -> entity edges, so chunks are predecessors of entity.
                for pred in self.graph.predecessors(ent_node):
                    chunk = self._chunk_from_node(pred)
                    if not chunk:
                        continue
                    dedupe_key = chunk["chunk_id"] or normalize_text(chunk["text"])
                    if dedupe_key and dedupe_key not in chunk_seen:
                        chunks.append(chunk)
                        chunk_seen.add(dedupe_key)
                        if len(chunks) >= max_chunks:
                            return chunks

                # traverse RELATED_TO entity edges (entity -> entity)
                for _, nbr, k, edata in self.graph.out_edges(ent_node, keys=True, data=True):
                    if edata.get("kind") != "RELATED_TO":
                        continue
                    if nbr not in visited:
                        visited.add(nbr)
                        next_frontier.append(nbr)

            frontier = next_frontier
            if not frontier:
                break

        return chunks

    def get_reasoning_paths(self, entity_ids: List[str], max_paths: int = 5) -> List[List[str]]:
        if len(entity_ids) < 2:
            return []

        # Build a simple undirected entity-only graph from RELATED_TO edges.
        undirected = nx.Graph()
        for u, v, data in self.graph.edges(data=True):
            if data.get("kind") != "RELATED_TO":
                continue
            if self.graph.nodes.get(u, {}).get("kind") == "entity" and self.graph.nodes.get(v, {}).get("kind") == "entity":
                undirected.add_edge(u, v)

        ent_nodes = [_node_id("entity", e) for e in entity_ids]
        paths: List[List[str]] = []
        for i in range(len(ent_nodes)):
            for j in range(i + 1, len(ent_nodes)):
                a, b = ent_nodes[i], ent_nodes[j]
                if not (undirected.has_node(a) and undirected.has_node(b)):
                    continue
                try:
                    path_nodes = nx.shortest_path(undirected, a, b)
                except Exception:
                    continue
                pretty = [n.split("entity:", 1)[1] if n.startswith("entity:") else n for n in path_nodes]
                paths.append(pretty)
                if len(paths) >= max_paths:
                    return paths
        return paths

    def keyword_fallback(self, query: str, max_chunks: int = 8) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        If entity match fails, do a lightweight keyword search over entity labels and chunk text.
        """
        q = normalize_text(query)
        if not q:
            return [], []

        tokens = [t for t in q.split(" ") if len(t) >= 3]
        if not tokens:
            return [], []

        matched_entities: List[str] = []
        for n, d in self.graph.nodes(data=True):
            if d.get("kind") != "entity":
                continue
            label = d.get("label", "")
            if any(t in label for t in tokens):
                matched_entities.append(d.get("entity_id", label))
                if len(matched_entities) >= 10:
                    break

        chunks: List[Dict[str, Any]] = []
        for n, d in self.graph.nodes(data=True):
            if d.get("kind") != "chunk":
                continue
            text = normalize_text(d.get("text", ""))
            if any(t in text for t in tokens):
                chunks.append(
                    {
                        "chunk_id": d.get("chunk_id"),
                        "doc_id": d.get("doc_id"),
                        "text": d.get("text", ""),
                    }
                )
                if len(chunks) >= max_chunks:
                    break

        # de-dupe entities
        seen: Set[str] = set()
        deduped: List[str] = []
        for e in matched_entities:
            if e not in seen:
                deduped.append(e)
                seen.add(e)
        return deduped, chunks


def get_connection() -> NetworkXGraphClient:
    client = NetworkXGraphClient()
    client.load_graph()
    return client
