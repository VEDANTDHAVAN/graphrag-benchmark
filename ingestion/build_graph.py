from collections import defaultdict

from pipelines.graphrag.graphrag_client import NetworkXGraphClient, normalize_text
from ingestion.entity_extraction import extract_entities

MAX_ENTITIES_PER_CHUNK = 12


def build_graph(doc_id: str, title: str, chunks: list[dict], entities: list[tuple[str, str]]):
    """
    Local GraphRAG graph builder using NetworkXGraphClient.

    Nodes:
    - Document
    - Chunk
    - Entity

    Edges:
    - Document -> Chunk: HAS_CHUNK
    - Chunk -> Entity: MENTIONS
    - Entity -> Entity: RELATED_TO (co-mentions, capped per chunk)
    """
    client = NetworkXGraphClient()
    client.load_graph()

    source_file = chunks[0].get("source_file", title) if chunks else title
    client.add_document(doc_id, title=title, source_file=source_file)

    entity_type_map = {normalize_text(name): entity_type for name, entity_type in entities}

    relations_edges = 0
    mentions_edges = 0
    co_mentions: dict[tuple[str, str], set[str]] = defaultdict(set)

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]
        client.add_chunk(chunk_id=chunk_id, doc_id=doc_id, text=text)

        # Extract entities from this chunk, cap to avoid relation explosion.
        chunk_entities_raw = [name for name, _ in extract_entities([text])]
        chunk_entities: list[str] = []
        seen = set()
        for name in chunk_entities_raw:
            ent = normalize_text(name)
            if not ent or ent in seen:
                continue
            chunk_entities.append(ent)
            seen.add(ent)
            if len(chunk_entities) >= MAX_ENTITIES_PER_CHUNK:
                break

        # Add entity nodes + mentions edges.
        for ent in chunk_entities:
            client.add_entity(ent, entity_type=entity_type_map.get(ent, "Concept"))
            client.add_mentions_edge(chunk_id=chunk_id, entity_id=ent)
            mentions_edges += 1

        # Record co-mentions for RELATED_TO edges.
        unique = sorted(set(chunk_entities))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                a, b = unique[i], unique[j]
                co_mentions[(a, b)].add(chunk_id)

    for (a, b), evidence_chunks in co_mentions.items():
        # Store one evidence chunk for this relation (keeps edges lean).
        evidence = next(iter(evidence_chunks)) if evidence_chunks else None
        client.add_related_edge(a, b, evidence_chunk_id=evidence)
        relations_edges += 1

    client.save_graph()

    return {
        "documents": 1,
        "chunks": len(chunks),
        "entities": len(entities),
        "mentions_edges": mentions_edges,
        "relations_edges": relations_edges,
    }

