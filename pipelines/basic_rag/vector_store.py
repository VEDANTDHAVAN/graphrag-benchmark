import os
from typing import Any, Dict, List, Optional

import chromadb

from pipelines.basic_rag.embedding import embed_text
from utils.paths import chroma_path

COLLECTION_NAME = "chunks"


class VectorStore:
    """
    ChromaDB-backed persistent vector store.

    Public API (used by ingestion/pipelines):
    - add_documents(chunk_records)
    - search(query, k=5, filters=None)

    Notes:
    - Uses chunk_id as the Chroma record id.
    - Stores chunk text as document, plus metadata fields.
    """

    def __init__(self):
        chroma_dir = chroma_path()
        os.makedirs(chroma_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=chroma_dir)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    @classmethod
    def load(cls, path: Optional[str] = None):
        # Keep signature stable; `path` is unused for Chroma.
        return cls()

    def add_documents(self, chunk_records: List[Dict[str, Any]]) -> int:
        if not chunk_records:
            return 0

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for record in chunk_records:
            chunk_id = record["chunk_id"]
            ids.append(chunk_id)
            documents.append(record["text"])
            metadatas.append(
                {
                    "doc_id": record.get("doc_id", ""),
                    "chunk_id": chunk_id,
                    "source_file": record.get("source_file", ""),
                    "page": record.get("page"),
                }
            )

        embeddings = embed_text(documents)
        embeddings_list = [e.tolist() for e in embeddings]

        # Chroma raises if ids already exist. For ingestion re-runs, upsert.
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings_list,
            metadatas=metadatas,
        )
        return len(ids)

    def search(self, query: str, k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_embedding = embed_text([query])[0].tolist()

        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters,
            include=["documents", "metadatas", "distances"],
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        out: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            record = dict(meta or {})
            record["text"] = doc
            record["score"] = float(dist) if dist is not None else None
            out.append(record)
        return out

    # Back-compat helpers (old FAISS codepaths)
    def search_text(self, query: str, k: int = 5):
        return self.search(query, k=k)
