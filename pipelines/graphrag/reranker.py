import re
from typing import Dict, List, Optional

import numpy as np

from pipelines.basic_rag.embedding import embed_text as basic_embed_text

STOPWORDS = {
    "about",
    "does",
    "from",
    "help",
    "into",
    "paper",
    "that",
    "the",
    "this",
    "what",
    "with",
}


def embed_text(text: str):
    return basic_embed_text([text or ""])[0]


def cosine_similarity(query_embedding, chunk_embedding) -> float:
    q = np.asarray(query_embedding, dtype=float)
    c = np.asarray(chunk_embedding, dtype=float)
    denom = np.linalg.norm(q) * np.linalg.norm(c)
    if denom == 0:
        return 0.0
    return float(np.dot(q, c) / denom)


def _lexical_score(query: str, text: str) -> float:
    query_tokens = [
        token
        for token in re.findall(r"\b[a-z0-9]{3,}\b", (query or "").lower())
        if token not in STOPWORDS
    ]
    if not query_tokens:
        return 0.0
    lowered = (text or "").lower()
    overlap = sum(1 for token in set(query_tokens) if token in lowered) / len(set(query_tokens))

    phrase_hits = 0
    phrases = []
    for size in (2, 3):
        for index in range(0, max(0, len(query_tokens) - size + 1)):
            phrases.append(" ".join(query_tokens[index : index + size]))
    for phrase in phrases:
        if phrase in lowered:
            phrase_hits += 1
    phrase_score = min(1.0, phrase_hits / max(1, min(4, len(phrases))))
    return min(1.0, (0.65 * overlap) + (0.35 * phrase_score))


def rerank_chunks(query: str, chunks: List[Dict], embedding_model: Optional[object] = None) -> List[Dict]:
    if not chunks:
        return []

    texts = [chunk.get("text", "") or "" for chunk in chunks]
    if embedding_model is not None:
        query_embedding = embedding_model.encode([query or ""])[0]
        chunk_embeddings = embedding_model.encode(texts)
    else:
        query_embedding = basic_embed_text([query or ""])[0]
        chunk_embeddings = basic_embed_text(texts)

    ranked: List[Dict] = []
    for chunk, chunk_embedding in zip(chunks, chunk_embeddings):
        item = dict(chunk)
        semantic_score = cosine_similarity(query_embedding, chunk_embedding)
        lexical_score = _lexical_score(query, item.get("text", ""))
        item["score"] = (0.8 * semantic_score) + (0.2 * lexical_score)
        item["semantic_score"] = semantic_score
        item["lexical_score"] = lexical_score
        item.setdefault("source", "graph_expansion")
        item.setdefault("graph_distance", 0 if item["source"] == "seed" else 1)
        ranked.append(
            {
                "chunk_id": item.get("chunk_id"),
                "doc_id": item.get("doc_id"),
                "text": item.get("text", ""),
                "score": item.get("score", 0.0),
                "source": item.get("source"),
                "graph_distance": item.get("graph_distance", 0),
                **{k: v for k, v in item.items() if k not in {"chunk_id", "doc_id", "text", "score", "source", "graph_distance"}},
            }
        )

    ranked.sort(key=lambda item: item.get("score", 0.0), reverse=True)
    return ranked
