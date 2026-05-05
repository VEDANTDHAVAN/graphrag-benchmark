from pipelines.basic_rag.vector_store import VectorStore


def main():
    store = VectorStore.load()
    col = store.collection
    count = col.count()
    settings = store.client.get_settings()
    persist_dir = getattr(settings, "persist_directory", None)
    print("chroma_path:", persist_dir or "data/chroma")
    print("collection:", col.name)
    print("count:", count)

    if count == 0:
        return

    sample = col.get(limit=min(5, count), include=["documents", "metadatas"])
    docs = sample.get("documents", [])
    metas = sample.get("metadatas", [])

    for i in range(len(docs)):
        meta = metas[i] if i < len(metas) else {}
        doc = docs[i] if i < len(docs) else ""
        preview = " ".join((doc or "").split())[:160]
        print(f"{i+1}. chunk_id={meta.get('chunk_id')} doc_id={meta.get('doc_id')} source_file={meta.get('source_file')} page={meta.get('page')}")
        print(f"   text={preview}")


if __name__ == "__main__":
    main()
