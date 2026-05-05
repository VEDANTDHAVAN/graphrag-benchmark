from utils.llm import generate

from .retriever import retrieve_graph_context

MAX_CONTEXT_CHARS = 1400
MAX_CHUNKS = 4


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


def run_graphrag(query):
    graph_context = retrieve_graph_context(query, k=MAX_CHUNKS, hops=2)
    chunks = graph_context.get("chunks", [])[:MAX_CHUNKS]

    keywords = list(dict.fromkeys((graph_context.get("matched_entities") or []) + (graph_context.get("query_entities") or [])))

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

    return {
        "status": "success",
        "answer": res["text"],
        "context": context,
        "tokens": res["total_tokens"],
        "latency": res["latency"],
        "details": graph_context,
    }
