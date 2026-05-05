from pipelines.graphrag.graphrag_client import get_connection
from ingestion.entity_extraction import extract_entities


def build_graph(doc_id, title, chunks, entities):
    """
    Legacy TigerGraph graph builder (kept for future compatibility).
    Not used in the local NetworkX GraphRAG pivot.
    """
    conn = get_connection()
    mention_edges = 0
    entity_ids = {entity_name for entity_name, _ in entities}

    conn.upsert_document(doc_id, title)

    for chunk in chunks:
        conn.upsert_chunk(chunk["chunk_id"], chunk["text"])
        conn.link_doc_chunk(doc_id, chunk["chunk_id"])

    for entity_name, entity_type in entities:
        entity_id = entity_name.lower()
        conn.upsert_entity(entity_id, entity_name, entity_type)

    for chunk in chunks:
        chunk_entities = extract_entities([chunk["text"]])
        for entity_name, _ in chunk_entities:
            if entity_name in entity_ids:
                conn.link_chunk_entity(chunk["chunk_id"], entity_name)
                mention_edges += 1

    return {
        "documents": 1,
        "chunks": len(chunks),
        "entities": len(entities),
        "has_chunk_edges": len(chunks),
        "mentions_edges": mention_edges,
    }

