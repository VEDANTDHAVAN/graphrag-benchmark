from utils.llm import generate

def run_llm_only(query):
    prompt = f"Answer the question:\n{query}"

    res = generate(prompt)

    return {
        "answer": res["text"],
        "context": "",
        "tokens": res["total_tokens"],
        "latency": res["latency"]
    }
