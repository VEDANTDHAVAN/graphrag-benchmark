import re

def chunk_text(text, chunk_size=2):
    # Split into sentences
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []

    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i + chunk_size])
        chunks.append(chunk.strip())

    return chunks