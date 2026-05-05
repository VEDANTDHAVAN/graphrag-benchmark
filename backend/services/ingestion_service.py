import uuid

from ingestion.preprocess import extract_text_from_file
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
    pages, file_type = extract_text_from_file(file_name, file_bytes)
    if not pages or not any(p.strip() for p in pages):
        raise ValueError("No extractable text found in file")

    # -------------------------
    # 2. CHUNKING
    # -------------------------
    chunk_records = []
    chunk_index = 0
    for page_num, page_text in enumerate(pages, start=1):
        if not page_text.strip():
            continue
        page_chunks = chunk_text(page_text)
        for chunk in page_chunks:
            chunk_records.append(
                {
                    "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                    "doc_id": doc_id,
                    "text": chunk,
                    "source_file": file_name,
                    "page": page_num if file_type == "pdf" else None,
                }
            )
            chunk_index += 1

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
