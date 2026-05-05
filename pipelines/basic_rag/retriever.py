def retrieve(query, vector_store, k=3):
    results = vector_store.search(query, k=k * 10)

    unique = []
    seen = set()

    for record in results:
        chunk_id = record.get("chunk_id")
        text = record.get("text", "")
        dedupe_key = " ".join(text.split()).lower() or chunk_id

        if dedupe_key not in seen:
            unique.append(record)
            seen.add(dedupe_key)

        if len(unique) == k:
            break

    return unique
