import requests
from utils.config_loader import Config

def ingest_graph():
    with open("data/processed/chunks.json") as f:
        data = f.read()

    response = requests.post(
        f"{Config.GRAPH_RAG_API_URL}/ingest",
        json={"documents": data}
    )

    print("Graph ingestion status:", response.status_code)

if __name__ == "__main__":
    ingest_graph()
