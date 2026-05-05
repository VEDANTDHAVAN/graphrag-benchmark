from pipelines.basic_rag.vector_store import VectorStore


def add_to_vector_store(chunk_records):
    """
    Real-time ingestion into persisted ChromaDB
    """
    if not chunk_records:
        raise ValueError("Cannot build embeddings for an empty document")

    store = VectorStore.load()
    store.add_documents(chunk_records)
    return None
