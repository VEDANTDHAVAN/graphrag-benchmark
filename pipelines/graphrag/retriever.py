import re
from typing import Dict, List, Tuple

from .graphrag_client import NetworkXGraphClient, normalize_text

STOPWORDS = {
    "about",
    "does",
    "from",
    "for",
    "paper",
    "that",
    "this",
    "what",
    "with",
}


def extract_query_entities(query: str) -> List[str]:
    tokens = []
    seen = set()
    for match in re.findall(r"\b[A-Za-z][A-Za-z0-9-]{2,}\b", query):
        normalized = normalize_text(match)
        if not normalized or normalized in STOPWORDS or normalized in seen:
            continue
        tokens.append(normalized)
        seen.add(normalized)
    return tokens


def _rank_chunks(query: str, chunks: List[Dict], limit: int) -> List[Dict]:
    tokens = [t for t in normalize_text(query).split(" ") if len(t) >= 3 and t not in STOPWORDS]
    if not tokens:
        return chunks[:limit]

    def score(chunk: Dict) -> tuple[int, int, int]:
        text = normalize_text(chunk.get("text", ""))
        overlap = sum(1 for token in tokens if token in text)
        title_bonus = 4 if overlap >= min(4, len(tokens)) and chunk.get("chunk_id", "").endswith("_chunk_0000") else 0
        phrase_bonus = 3 if normalize_text(query)[:80] in text else 0
        return overlap + title_bonus + phrase_bonus, overlap, len(text)

    ranked = sorted(chunks, key=score, reverse=True)
    out = []
    seen = set()
    for chunk in ranked:
        key = chunk.get("chunk_id") or normalize_text(chunk.get("text", ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(chunk)
        if len(out) >= limit:
            break
    return out


def retrieve_graph_context(
    query: str,
    k: int = 8,
    hops: int = 2,
) -> Dict:
    client = NetworkXGraphClient()
    graph = client.load_graph()

    diagnostics = {
        "graph_loaded": bool(graph.number_of_nodes()),
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "graph_path": client.graph_path,
    }

    query_entities = extract_query_entities(query)
    matched_entities = client.search_entities(query_entities)

    if matched_entities:
        candidates = client.get_neighbor_chunks(matched_entities, hops=hops, max_chunks=max(k * 8, 32))
        _, lexical_candidates = client.keyword_fallback(query, max_chunks=max(k * 8, 32))
        candidates = [*lexical_candidates, *candidates]
        chunks = _rank_chunks(query, candidates, k)
        reasoning_paths = client.get_reasoning_paths(matched_entities, max_paths=5)
        return {
            "query_entities": query_entities,
            "matched_entities": matched_entities,
            "chunks": chunks,
            "reasoning_paths": reasoning_paths,
            "diagnostics": diagnostics,
        }

    # Fallback: keyword search over entity labels + chunk text.
    fallback_entities, fallback_candidates = client.keyword_fallback(query, max_chunks=max(k * 8, 32))
    fallback_chunks = _rank_chunks(query, fallback_candidates, k)
    reasoning_paths = client.get_reasoning_paths(fallback_entities, max_paths=5) if fallback_entities else []

    diagnostics["fallback"] = "keyword"

    return {
        "query_entities": query_entities,
        "matched_entities": fallback_entities,
        "chunks": fallback_chunks,
        "reasoning_paths": reasoning_paths,
        "diagnostics": diagnostics,
    }
