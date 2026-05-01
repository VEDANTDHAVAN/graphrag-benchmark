import time
from utils.token_counter import count_tokens

def call_llm(prompt: str) -> str:
    # Replace with real API call
    return f"[LLM Answer] {prompt}"

def run_llm_only(query: str):
    start = time.time()

    prompt = f"Answer the question:\n{query}"
    answer = call_llm(prompt)

    latency = time.time() - start
    tokens = count_tokens(prompt + answer)

    return {
        "answer": answer,
        "tokens": tokens,
        "latency": latency
    }
