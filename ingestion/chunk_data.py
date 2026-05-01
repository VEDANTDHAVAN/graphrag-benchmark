import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipelines.basic_rag.chunking import chunk_text

INPUT_DIR = "data/processed"
OUTPUT_FILE = "data/processed/chunks.json"

import json

def run_chunking():
    all_chunks = []

    for file in os.listdir(INPUT_DIR):
        with open(f"{INPUT_DIR}/{file}") as f:
            text = f.read()

        chunks = chunk_text(text)
        
        for c in chunks:
            all_chunks.append({
                "source": file,
                "text": c
            })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_chunks, f)

if __name__ == "__main__":
    run_chunking()
