import logging
from typing import Any, Dict, List, Optional, Set

import networkx as nx

from pipelines.basic_rag.vector_store import VectorStore
from pipelines.shared.token_utils import select_under_budget

from .graph_utils import (
    collect_subgraph_trace,
    find_chunk_node,
    get_connected_entities,
    get_neighbor_chunks,
    load_graph,
)
from .reranker import rerank_chunks

logger = logging.getLogger(__name__)


class HybridGraphRetriever:
    def __init__(
        self,
        vector_store: Optional[Any] = None,
        graph: Optional[nx.MultiDiGraph] = None,
        embedding_model: Optional[Any] = None,
        top_k_seed: int = 8,
        graph_hops: int = 1,
        max_expanded_nodes: int = 40,
        final_top_k: int = 4,
        min_similarity_threshold: float = 0.25,
        token_budget: int = 1200,
    ):
        self.vector_store = vector_store or VectorStore.load()
        self.graph = graph
        self.embedding_model = embedding_model
        self.top_k_seed = top_k_seed
        self.graph_hops = graph_hops
        self.max_expanded_nodes = max_expanded_nodes
        self.final_top_k = final_top_k
        self.min_similarity_threshold = min_similarity_threshold
        self.token_budget = token_budget

    def retrieve(self, query: str) -> Dict[str, Any]:
        seed_chunks = self._seed_chunks(query)
        fallback_reason = ""
        fallback_used = False
        seed_nodes: List[str] = []
        expanded_nodes: List[str] = []
        graph_candidates: List[Dict] = []
        trace_edges: List[Dict] = []

        try:
            graph = self.graph if self.graph is not None else load_graph()
            for chunk in seed_chunks:
                node_id = find_chunk_node(graph, chunk.get("chunk_id", ""))
                if not node_id:
                    continue
                seed_nodes.append(node_id)
                neighbors = get_neighbor_chunks(graph, node_id, hops=self.graph_hops)
                for neighbor in neighbors:
                    if len(expanded_nodes) >= self.max_expanded_nodes:
                        break
                    if neighbor.get("node_id"):
                        expanded_nodes.append(neighbor["node_id"])
                    graph_candidates.append(neighbor)

            if not seed_nodes:
                fallback_used = True
                fallback_reason = "no_seed_graph_nodes"

            subgraph = collect_subgraph_trace(graph, seed_nodes, expanded_nodes)
            trace_edges = subgraph.get("edges", [])
        except Exception as exc:
            logger.exception("Hybrid GraphRAG graph expansion failed")
            fallback_used = True
            fallback_reason = f"graph_exception:{exc.__class__.__name__}"
            graph_candidates = []
            expanded_nodes = []
            trace_edges = []

        candidates = self._dedupe_candidates([*seed_chunks, *graph_candidates])
        reranked_candidates = rerank_chunks(query, candidates, embedding_model=self.embedding_model)
        graph_scores = [
            item.get("score", 0.0)
            for item in reranked_candidates
            if item.get("source") == "graph_expansion"
        ]

        if not graph_candidates and not fallback_used:
            fallback_used = True
            fallback_reason = "empty_graph_expansion"
        elif graph_scores and max(graph_scores) < self.min_similarity_threshold and not fallback_used:
            fallback_used = True
            fallback_reason = "low_graph_similarity"

        selection_pool = seed_chunks if fallback_used else reranked_candidates
        selected_contexts = select_under_budget(selection_pool[: self.final_top_k * 3], self.token_budget)
        selected_contexts = selected_contexts[: self.final_top_k]

        retrieval_trace = {
            "mode": "hybrid_graphrag",
            "seed_count": len(seed_chunks),
            "seed_chunk_ids": [c.get("chunk_id") for c in seed_chunks],
            "expanded_node_count": len(set(expanded_nodes)),
            "expanded_edge_count": len(trace_edges),
            "reranked_candidate_count": len(reranked_candidates),
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
            "graph_hops": self.graph_hops,
            "selected_chunk_ids": [c.get("chunk_id") for c in selected_contexts],
            "top_scores": [round(float(c.get("score", 0.0)), 4) for c in reranked_candidates[:5]],
        }

        logger.info(
            "hybrid_graphrag query=%r seeds=%s expanded_nodes=%s candidates=%s top_scores=%s fallback=%s selected=%s",
            query,
            retrieval_trace["seed_chunk_ids"],
            retrieval_trace["expanded_node_count"],
            retrieval_trace["reranked_candidate_count"],
            retrieval_trace["top_scores"],
            fallback_used,
            retrieval_trace["selected_chunk_ids"],
        )

        return {
            "selected_contexts": selected_contexts,
            "seed_chunks": seed_chunks,
            "expanded_nodes": list(dict.fromkeys(expanded_nodes)),
            "expanded_edges": trace_edges,
            "reranked_candidates": reranked_candidates,
            "fallback_used": fallback_used,
            "retrieval_trace": retrieval_trace,
            "connected_entities": self._connected_entities(seed_chunks),
        }

    def _seed_chunks(self, query: str) -> List[Dict]:
        raw = self.vector_store.search(query, k=self.top_k_seed)
        seeds: List[Dict] = []
        seen: Set[str] = set()
        for item in raw:
            chunk_id = item.get("chunk_id")
            text_key = " ".join((item.get("text") or "").split()).lower()
            key = chunk_id or text_key
            if not key or key in seen:
                continue
            seen.add(key)
            seed = dict(item)
            seed["source"] = "seed"
            seed["graph_distance"] = 0
            seeds.append(seed)
        return seeds

    def _dedupe_candidates(self, chunks: List[Dict]) -> List[Dict]:
        out: List[Dict] = []
        seen: Set[str] = set()
        for chunk in chunks:
            key = chunk.get("chunk_id") or " ".join((chunk.get("text") or "").split()).lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(chunk)
        return out

    def _connected_entities(self, seed_chunks: List[Dict]) -> List[Dict]:
        try:
            graph = self.graph if self.graph is not None else load_graph()
            entities: List[Dict] = []
            seen: Set[str] = set()
            for chunk in seed_chunks:
                for entity in get_connected_entities(graph, chunk.get("chunk_id", "")):
                    key = entity.get("entity_id") or entity.get("node_id")
                    if key in seen:
                        continue
                    seen.add(key)
                    entities.append(entity)
            return entities
        except Exception:
            return []
