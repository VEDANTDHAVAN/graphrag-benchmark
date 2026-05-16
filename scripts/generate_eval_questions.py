from collections import defaultdict

from benchmark_utils import (
    EVAL_QUESTIONS_PATH,
    RAW_DATASET_PATH,
    first_sentence,
    iter_jsonl,
    top_terms,
    write_json,
)


def main() -> None:
    docs = list(iter_jsonl(RAW_DATASET_PATH))
    if not docs:
        raise FileNotFoundError(f"No corpus rows found in {RAW_DATASET_PATH}")

    selected = diverse_docs(docs, 40)
    questions = []
    questions.extend(factual_questions(selected[:10]))
    questions.extend(entity_questions(selected[10:20]))
    questions.extend(multihop_questions(selected[20:30]))
    questions.extend(synthesis_questions(selected[30:40]))

    write_json(EVAL_QUESTIONS_PATH, questions[:40])
    print(f"Saved {len(questions[:40])} questions to {EVAL_QUESTIONS_PATH}")


def diverse_docs(docs, count):
    with_abstract = [doc for doc in docs if doc.get("abstract") and doc.get("title")]
    return with_abstract[:count] if len(with_abstract) >= count else docs[:count]


def factual_questions(docs):
    out = []
    for doc in docs:
        title = doc.get("title", doc["doc_id"])
        abstract = doc.get("abstract", "")
        answer = first_sentence(abstract) or f"The paper titled {title} is part of the benchmark corpus."
        out.append(
            {
                "question": f"What is the main contribution or focus of the paper titled '{title}'?",
                "correct_answer": answer,
                "expected_entities": top_terms(title + " " + abstract, 4),
                "difficulty": "easy",
                "category": "factual",
                "source_doc_ids": [doc["doc_id"]],
            }
        )
    return out


def entity_questions(docs):
    out = []
    for doc in docs:
        title = doc.get("title", doc["doc_id"])
        terms = top_terms(doc.get("abstract", "") + " " + doc.get("article", ""), 6)
        focus = terms[0] if terms else "the proposed approach"
        answer_terms = ", ".join(terms[:4]) if terms else title
        out.append(
            {
                "question": f"In '{title}', which methods, tasks, or concepts are most closely associated with {focus}?",
                "correct_answer": f"The paper associates {focus} with these grounded concepts: {answer_terms}.",
                "expected_entities": terms[:5],
                "difficulty": "medium",
                "category": "entity",
                "source_doc_ids": [doc["doc_id"]],
            }
        )
    return out


def multihop_questions(docs):
    groups = group_by_shared_term(docs)
    pairs = []
    for term, term_docs in groups.items():
        if len(term_docs) >= 2:
            pairs.append((term, term_docs[0], term_docs[1]))
        if len(pairs) >= 10:
            break

    while len(pairs) < 10 and len(docs) >= 2:
        i = len(pairs) * 2
        pairs.append(("scientific modeling", docs[i % len(docs)], docs[(i + 1) % len(docs)]))

    out = []
    for term, a, b in pairs[:10]:
        answer = (
            f"Both papers discuss {term}. '{a.get('title', a['doc_id'])}' frames it around "
            f"{', '.join(top_terms(a.get('abstract', ''), 3)) or 'its stated research problem'}, while "
            f"'{b.get('title', b['doc_id'])}' connects it to "
            f"{', '.join(top_terms(b.get('abstract', ''), 3)) or 'its stated research problem'}."
        )
        out.append(
            {
                "question": (
                    f"How do the papers '{a.get('title', a['doc_id'])}' and "
                    f"'{b.get('title', b['doc_id'])}' connect through {term}?"
                ),
                "correct_answer": answer,
                "expected_entities": list({term, *top_terms(a.get("abstract", ""), 2), *top_terms(b.get("abstract", ""), 2)}),
                "difficulty": "hard",
                "category": "multihop",
                "source_doc_ids": [a["doc_id"], b["doc_id"]],
            }
        )
    return out


def synthesis_questions(docs):
    out = []
    for doc in docs:
        title = doc.get("title", doc["doc_id"])
        terms = top_terms(doc.get("abstract", "") + " " + doc.get("article", ""), 5)
        answer = (
            f"A concise synthesis of '{title}' is that it studies {', '.join(terms[:3]) or 'the paper topic'} "
            f"and supports that focus with the abstract claim: {first_sentence(doc.get('abstract', ''))}"
        )
        out.append(
            {
                "question": f"Synthesize the research problem, approach, and likely significance of '{title}'.",
                "correct_answer": answer,
                "expected_entities": terms,
                "difficulty": "hard",
                "category": "synthesis",
                "source_doc_ids": [doc["doc_id"]],
            }
        )
    return out


def group_by_shared_term(docs):
    groups = defaultdict(list)
    for doc in docs:
        for term in top_terms(doc.get("abstract", ""), 5):
            groups[term].append(doc)
    return groups


if __name__ == "__main__":
    main()
