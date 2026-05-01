import time
from utils.token_counter import count_tokens
from .graphrag_client import query_graphrag

def run_graphrag(query: str):
    start = time.time()

    response = query_graphrag(query)
    answer = response.get("answer", "")

    latency = time.time() - start
    tokens = count_tokens(query + answer)

    return {
        "answer": answer,
        "tokens": tokens,
        "latency": latency
    }
