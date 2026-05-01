import faiss
import numpy as np
import pickle
import os

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings))
        self.texts.extend(texts)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(query_embedding, k)
        return [self.texts[i] for i in I[0]]

    def save(self, path_prefix):
        faiss.write_index(self.index, f"{path_prefix}.index")
        with open(f"{path_prefix}.pkl", "wb") as f:
            pickle.dump(self.texts, f)

    @classmethod
    def load(cls, path_prefix):
        if not os.path.exists(f"{path_prefix}.index"):
            raise FileNotFoundError("Vector store not found. Run ingestion first.")

        index = faiss.read_index(f"{path_prefix}.index")
        with open(f"{path_prefix}.pkl", "rb") as f:
            texts = pickle.load(f)

        store = cls(index.d)
        store.index = index
        store.texts = texts
        return store