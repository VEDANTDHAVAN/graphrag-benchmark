import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evaluation.evaluator import evaluate, evaluate_batch


def _load_json(path, fallback):
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else fallback
    except (OSError, json.JSONDecodeError):
        return fallback


def _load_ground_truth(path):
    data = _load_json(path, [])
    if isinstance(data, list):
        return [
            {
                "question": row.get("question", row.get("query", "")),
                "correct_answer": row.get("correct_answer", row.get("answer", "")),
            }
            for row in data
        ]

    if isinstance(data, dict):
        return [
            {"question": question, "correct_answer": correct_answer}
            for question, correct_answer in data.items()
        ]

    return []

def run():
    queries = _load_json("experiments/queries.json", [])
    ground_truth_rows = _load_ground_truth("evaluation/ground_truth.json")
    ground_truth_by_question = {
        row["question"]: row["correct_answer"]
        for row in ground_truth_rows
        if row.get("question")
    }

    results = []
    batch_answers = {
        "llm_only": [],
        "basic_rag": [],
        "graphrag": [],
    }
    batch_truth = []

    for q in queries:
        query = q.get("query", q.get("question", ""))
        if not query:
            continue

        from pipelines.llm_only.llm_pipeline import run_llm_only
        from pipelines.basic_rag.rag_pipeline import run_basic_rag
        from pipelines.graphrag.graphrag_pipeline import run_graphrag

        llm = run_llm_only(query)
        rag = run_basic_rag(query)
        graph = run_graphrag(query)

        outputs = {
            "llm_only": llm,
            "basic_rag": rag,
            "graphrag": graph
        }

        correct_answer = ground_truth_by_question.get(query, q.get("correct_answer", ""))
        eval_res = evaluate(query, outputs, correct_answer)

        results.append({"query": query, "results": eval_res})

        if correct_answer:
            batch_truth.append({"question": query, "correct_answer": correct_answer})
            for pipeline_name, output in outputs.items():
                batch_answers[pipeline_name].append(output.get("answer", ""))

    summary = evaluate_batch(batch_answers, batch_truth) if batch_truth else {}
    combined = {
        "summary": summary,
        "results": results,
    }

    with open("experiments/results/combined_results.json", "w") as f:
        json.dump(combined, f, indent=2)

if __name__ == "__main__":
    run()
