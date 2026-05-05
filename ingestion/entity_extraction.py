import re

STOPWORDS = {
    "about",
    "after",
    "also",
    "because",
    "being",
    "between",
    "could",
    "does",
    "from",
    "for",
    "have",
    "into",
    "more",
    "other",
    "paper",
    "than",
    "that",
    "their",
    "there",
    "these",
    "this",
    "through",
    "using",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def extract_entities(chunks):
    entities = set()

    for text in chunks:
        words = re.findall(r"\b[A-Z][A-Za-z0-9]*(?:-[A-Z0-9][A-Za-z0-9]*)*\b", text)
        words.extend(re.findall(r"\b[a-z][a-z0-9-]{4,}\b", text))

        for w in words:
            normalized = w.strip("-").lower()
            if normalized and normalized not in STOPWORDS:
                entities.add((normalized, "Concept"))

    return list(entities)
