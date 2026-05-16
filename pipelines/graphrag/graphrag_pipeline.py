from utils.llm import generate

from .hybrid_retriever import HybridGraphRetriever

MAX_CONTEXT_CHARS = 1400
MAX_CHUNKS = 4
HYBRID_RETRIEVER = None


def _split_sentences(text: str):
    # Lightweight sentence splitter; good enough for evidence extraction.
    parts = []
    buf = []
    for ch in text:
        buf.append(ch)
        if ch in ".!?":
            s = "".join(buf).strip()
            if s:
                parts.append(s)
            buf = []
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _evidence_snippet(text: str, keywords: list[str], max_sentences: int = 2) -> str:
    if not text:
        return ""
    lowered = text.lower()
    if not keywords:
        return " ".join(text.split())[:400]

    sentences = _split_sentences(text)
    hits = []
    for s in sentences:
        sl = s.lower()
        if any(k in sl for k in keywords):
            hits.append(s.strip())
        if len(hits) >= max_sentences:
            break

    if hits:
        return " ".join(hits)
    # fallback: first ~300 chars
    return " ".join(text.split())[:300]


def get_hybrid_retriever():
    global HYBRID_RETRIEVER
    if HYBRID_RETRIEVER is None:
        HYBRID_RETRIEVER = HybridGraphRetriever(
            top_k_seed=8,
            graph_hops=1,
            max_expanded_nodes=40,
            final_top_k=MAX_CHUNKS,
            min_similarity_threshold=0.25,
            token_budget=1200,
        )
    return HYBRID_RETRIEVER


def run_graphrag(query):
    graph_context = get_hybrid_retriever().retrieve(query)
    chunks = graph_context.get("selected_contexts", [])[:MAX_CHUNKS]

    entity_labels = [
        item.get("label") or item.get("name") or item.get("entity_id")
        for item in graph_context.get("connected_entities", [])
    ]
    keywords = list(dict.fromkeys([k for k in entity_labels if k]))

    context = "\n\n".join(
        f"[{i + 1}] { _evidence_snippet(chunk.get('text', ''), keywords) }"
        for i, chunk in enumerate(chunks)
    )
    context = context[:MAX_CONTEXT_CHARS]

    prompt = f"""Answer the question using ONLY the provided graph context.
If the context is insufficient, say so.

Graph context:
{context or "No graph context retrieved."}

Question:
{query}

Answer:"""

    res = generate(prompt)

    if not chunks:
        diag = graph_context.get("diagnostics", {})
        diag["hint"] = (
            "Graph context empty. Check data/graph/graphrag_graph.pkl and re-upload/re-ingest documents."
        )
        graph_context["diagnostics"] = diag

    retrieval_trace = graph_context.get("retrieval_trace", {})
    details = {
        **graph_context,
        "chunks": chunks,
        "retrieved_chunks": chunks,
        "matched_entities": [
            item.get("label") or item.get("name") or item.get("entity_id")
            for item in graph_context.get("connected_entities", [])
        ],
        "reasoning_paths": [],
        "retrieval_trace": retrieval_trace,
        "graph_nodes_used": retrieval_trace.get("expanded_node_count", 0),
        "graph_edges_used": retrieval_trace.get("expanded_edge_count", 0),
        "seed_chunks_used": retrieval_trace.get("seed_count", 0),
        "fallback_used": retrieval_trace.get("fallback_used", False),
        "reranked_candidate_count": retrieval_trace.get("reranked_candidate_count", 0),
        "prompt_tokens": res.get("prompt_tokens", 0),
        "completion_tokens": res.get("completion_tokens", 0),
    }

    return {
        "status": "success",
        "answer": res["text"],
        "context": context,
        "context_used": chunks,
        "tokens": res["total_tokens"],
        "latency": res["latency"],
        "retrieval_trace": retrieval_trace,
        "details": details,
    }
