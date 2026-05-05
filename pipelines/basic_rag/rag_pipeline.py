from .retriever import retrieve
from .vector_store import VectorStore
from utils.llm import generate

VECTOR_STORE = None
MAX_CONTEXT_CHARS = 2500
OVERVIEW_TERMS = (
    "what is this paper about",
    "what is the paper about",
    "summarize the paper",
    "summary of the paper",
    "paper summary",
    "abstract",
    "main idea",
)


def get_store():
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = VectorStore.load()
    return VECTOR_STORE


def _chunk_number(record):
    chunk_id = record.get("chunk_id", "")
    try:
        return int(chunk_id.rsplit("_chunk_", 1)[1])
    except (IndexError, ValueError):
        return 10**9


def _is_overview_query(query):
    normalized = " ".join(query.lower().split())
    return any(term in normalized for term in OVERVIEW_TERMS)


def _overview_chunks(store, limit=3):
    # Chroma doesn't expose raw metadata list like the old FAISS store.
    # Overview queries will rely on semantic retrieval for now.
    return []


def _merge_chunks(primary, secondary, limit=5):
    merged = []
    seen = set()

    for record in [*primary, *secondary]:
        text = record.get("text", "")
        dedupe_key = " ".join(text.split()).lower() or record.get("chunk_id")
        if dedupe_key not in seen:
            merged.append(record)
            seen.add(dedupe_key)

        if len(merged) == limit:
            break

    return merged


def run_basic_rag(query):
    store = get_store()
    semantic_chunks = retrieve(query, store, k=3)
    if _is_overview_query(query):
        retrieved_chunks = _merge_chunks(_overview_chunks(store), semantic_chunks)
    else:
        retrieved_chunks = semantic_chunks

    context = "\n\n".join(
        f"[{i + 1}] {chunk.get('text', '')}"
        for i, chunk in enumerate(retrieved_chunks)
    )
    context = context[:MAX_CONTEXT_CHARS]

    prompt = f"""
You are an AI assistant.

Use ONLY the provided context to answer the question.
If the context does not contain enough information, say so.

Context:
{context}

Question:
{query}

Answer:
"""

    res = generate(prompt)

    return {
        "answer": res["text"],
        "context": context,
        "tokens": res["total_tokens"],
        "latency": res["latency"],
        "details": {
            "prompt_tokens": res["prompt_tokens"],
            "completion_tokens": res["completion_tokens"],
            "retrieved_chunks": retrieved_chunks,
        },
    }
