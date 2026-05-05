from pathlib import Path

from pipelines.graphrag.graphrag_client import NetworkXGraphClient


def main():
    client = NetworkXGraphClient()
    graph = client.load_graph()
    stats = client.stats()

    print("graph_path:", stats.graph_path)
    print("graph_loaded:", stats.graph_loaded)
    print("node_count:", stats.node_count)
    print("edge_count:", stats.edge_count)

    entity_labels = []
    chunk_texts = []

    for _, data in graph.nodes(data=True):
        if data.get("kind") == "entity":
            entity_labels.append(data.get("label") or data.get("entity_id"))
        elif data.get("kind") == "chunk":
            text = data.get("text", "")
            chunk_texts.append(text)

    print("first_20_entities:", entity_labels[:20])
    print("first_10_chunks:")
    for i, text in enumerate(chunk_texts[:10]):
        preview = " ".join(text.split())[:160]
        print(f"{i+1}. {preview}")


if __name__ == "__main__":
    main()

