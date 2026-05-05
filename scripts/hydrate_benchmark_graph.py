from collections import defaultdict

from pipelines.basic_rag.vector_store import VectorStore
from ingestion.entity_extraction import extract_entities
from ingestion.build_graph import build_graph


def chunk_index(chunk_id: str) -> int:
    if "_chunk_" not in chunk_id:
        return 0
    try:
        return int(chunk_id.rsplit("_chunk_", 1)[1])
    except ValueError:
        return 0


def main():
    store = VectorStore.load()

    by_doc = defaultdict(list)
    for record in store.metadata:
        by_doc[record["doc_id"]].append(record)

    for doc_id, chunks in by_doc.items():
        chunks.sort(key=lambda r: chunk_index(r["chunk_id"]))
        entities = extract_entities([chunk["text"] for chunk in chunks])
        result = build_graph(
            doc_id=doc_id,
            title=f"Imported document {doc_id}",
            chunks=chunks,
            entities=entities,
        )
        print(doc_id, result)


if __name__ == "__main__":
    main()

