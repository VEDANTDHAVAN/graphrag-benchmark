from .vector_store import VectorStore
from .retriever import retrieve
import time

STORE_PATH = "data/embeddings/store"
VECTOR_STORE = None


def get_store():
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = VectorStore.load(STORE_PATH)
    return VECTOR_STORE


def call_llm(prompt):
    # Simulated reasoning (replace later with real LLM)
    if "Company B was involved in a fraud case" in prompt:
        return "Yes. Company A is indirectly linked to fraud through Company B."
    return "No clear connection found."


def run_basic_rag(query):
    store = get_store()

    start = time.time()

    # 🔍 Retrieve documents
    docs = retrieve(query, store, k=3)

    # 🧪 DEBUG (keep for now)
    print("\n[DEBUG - RAG Retrieved Docs]")
    for i, d in enumerate(docs):
        print(f"{i+1}: {d}")

    MAX_CONTEXT_CHARS = 500 

    # 📄 Build context
    context = "\n".join(docs)
    context = context[:MAX_CONTEXT_CHARS]

    prompt = f"""
You are an AI assistant.

Use ONLY the provided context to answer the question.

Context:
{context}

Question:
{query}

Answer:
"""

    # 🧠 Simulated LLM
    answer = call_llm(prompt)

    latency = time.time() - start

    # 🔢 Token estimation (better than before)
    prompt_tokens = len(prompt.split())
    answer_tokens = len(answer.split())
    total_tokens = prompt_tokens + answer_tokens

    return {
        "answer": f"[RAG]\n\nContext Used:\n{context}\n\nFinal Answer:\n{answer}",
        "tokens": total_tokens,
        "latency": latency,
        "details": {
            "prompt_tokens": prompt_tokens,
            "answer_tokens": answer_tokens,
            "retrieved_docs": docs
        }
    }
