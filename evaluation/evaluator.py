from .metrics import compute_cost
from .llm_judge import judge_answer

def evaluate(query, outputs, ground_truth):
    results = {}

    for name, out in outputs.items():
        results[name] = {
            "answer": out["answer"],
            "tokens": out["tokens"],
            "latency": out["latency"],
            "cost": compute_cost(out["tokens"]),
            "judge": judge_answer(out["answer"], ground_truth)
        }

    return results
