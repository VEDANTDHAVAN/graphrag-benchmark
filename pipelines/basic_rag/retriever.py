from .embedding import embed_text

def retrieve(query, vector_store, k=3):
    q_emb = embed_text([query])
    results = vector_store.search(q_emb, k * 2) # fetch extra

    # remove duplicates
    unique = []
    seen = set()

    for r in results:
        if r not in seen:
            unique.append(r)
            seen.add(r)

        if len(unique) == k:
            break

    return unique