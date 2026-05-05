import uuid

from ingestion.preprocess import extract_text_from_pdf
from ingestion.chunk_data import chunk_text
from ingestion.build_embeddings import add_to_vector_store
from ingestion.entity_extraction import extract_entities
from ingestion.build_graph import build_graph


async def ingest_document(file_name: str, file_bytes: bytes):
    """
    Unified ingestion for:
    - Basic RAG (vector store)
    - GraphRAG (local NetworkX graph)
    """

    doc_id = str(uuid.uuid4())

    # -------------------------
    # 1. PREPROCESS
    # -------------------------
    text = extract_text_from_pdf(file_bytes)
    if not text.strip():
        raise ValueError("No extractable text found in PDF")

    # -------------------------
    # 2. CHUNKING
    # -------------------------
    chunks = chunk_text(text)

    chunk_records = [
        {
            "chunk_id": f"{doc_id}_chunk_{i}",
            "doc_id": doc_id,
            "text": chunk,
            "source_file": file_name,
        }
        for i, chunk in enumerate(chunks)
    ]

    # -------------------------
    # 3. EMBEDDING + STORE (ONLY ONCE)
    # -------------------------
    add_to_vector_store(chunk_records)

    # -------------------------
    # 4. GRAPH RAG PIPELINE
    # -------------------------
    entities = extract_entities([c["text"] for c in chunk_records])

    graph_result = build_graph(
        doc_id=doc_id,
        title=file_name,
        chunks=chunk_records,
        entities=entities
    )

    # -------------------------
    # RETURN METADATA
    # -------------------------
    return {
        "status": "success",
        "doc_id": doc_id,
        "chunks_count": len(chunk_records),
        "entities_count": len(entities),
        "relations_count": graph_result.get("relations_edges", 0),
    }
