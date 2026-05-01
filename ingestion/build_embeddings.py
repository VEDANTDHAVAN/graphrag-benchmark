import json
import os
from pipelines.basic_rag.embedding import embed_text
from pipelines.basic_rag.vector_store import VectorStore

INPUT_FILE = "data/processed/chunks.json"
OUTPUT_DIR = "data/embeddings"
STORE_PATH = os.path.join(OUTPUT_DIR, "store")

def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading chunks...")
    data = json.load(open(INPUT_FILE))
    texts = [d["text"] for d in data]

    print(f"Total chunks: {len(texts)}")

    print("Generating embeddings...")
    embeddings = embed_text(texts)

    print("Building FAISS index...")
    store = VectorStore(dim=len(embeddings[0]))
    store.add(embeddings, texts)

    print("Saving vector store...")
    store.save(STORE_PATH)

    print("Embeddings built & saved successfully!!")

if __name__ == "__main__":
    build()