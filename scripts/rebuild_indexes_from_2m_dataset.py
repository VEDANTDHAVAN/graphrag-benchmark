import os
import shutil
from pathlib import Path

from benchmark_utils import RAW_DATASET_PATH, combined_doc_text, iter_jsonl

from ingestion.build_embeddings import add_to_vector_store
from ingestion.build_graph import build_graph
from ingestion.chunk_data import chunk_text
from ingestion.entity_extraction import extract_entities
from pipelines.graphrag.graphrag_client import NetworkXGraphClient
from utils.paths import chroma_path, graph_path


def main() -> None:
    if not RAW_DATASET_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {RAW_DATASET_PATH}")

    chroma_dir = Path(chroma_path())
    graph_file = Path(graph_path())

    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
    if graph_file.exists():
        graph_file.unlink()

    summary = {
        "documents": 0,
        "chunks": 0,
        "embeddings": 0,
        "graph_nodes": 0,
        "graph_edges": 0,
    }

    tigergraph_enabled = (
        os.getenv("REBUILD_TIGERGRAPH", "").lower() in {"1", "true", "yes"}
        or os.getenv("TIGERGRAPH_ENABLED", "false").lower() in {"1", "true", "yes"}
    )
    tg_builder = None
    if tigergraph_enabled:
        try:
            from ingestion.build_graph_tigergraph import build_graph as tg_builder
        except Exception as exc:
            print(f"TigerGraph reload disabled: {exc}")

    for doc in iter_jsonl(RAW_DATASET_PATH):
        doc_id = doc["doc_id"]
        title = doc.get("title", doc_id)
        text = combined_doc_text(doc)
        chunks = [
            {
                "chunk_id": f"{doc_id}_chunk_{i:04d}",
                "doc_id": doc_id,
                "text": chunk,
                "source_file": f"{doc_id}.jsonl",
                "page": None,
            }
            for i, chunk in enumerate(chunk_text(text, chunk_size=2000, overlap=200))
            if chunk.strip()
        ]
        if not chunks:
            continue

        entities = extract_entities([chunk["text"] for chunk in chunks])
        summary["documents"] += 1
        summary["chunks"] += len(chunks)
        summary["embeddings"] += add_to_vector_store(chunks) or len(chunks)
        build_graph(doc_id, title, chunks, entities)

        if tg_builder:
            try:
                tg_builder(doc_id, title, chunks, entities)
            except Exception as exc:
                print(f"TigerGraph reload skipped for {doc_id}: {exc}")
                tg_builder = None

    client = NetworkXGraphClient()
    graph = client.load_graph()
    summary["graph_nodes"] = graph.number_of_nodes()
    summary["graph_edges"] = graph.number_of_edges()

    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
