import requests
from utils.config_loader import Config 

def query_graphrag(query: str):
    return {
        "answer": f"[GraphRAG simulated answer] {query}"
    }