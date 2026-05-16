from .bertscore_eval import compute_bertscore
from .llm_judge import judge_answer, judge_answers
from .metrics import compute_cost

def evaluate(query, outputs, ground_truth):
    results = {}

    for name, out in outputs.items():
        answer = out.get("answer", "")
        tokens = out.get("tokens", 0)
        latency = out.get("latency", 0)
        results[name] = {
            "answer": answer,
            "tokens": tokens,
            "latency": latency,
            "cost": compute_cost(tokens),
            "judge": judge_answer(answer, ground_truth, query)
        }

    return results


def evaluate_single_answer(question, correct_answer, system_answer):
    verdict = judge_answer(system_answer, correct_answer, question)
    bert = compute_bertscore([system_answer], [correct_answer])
    return {
        "llm_judge": verdict,
        "llm_judge_pass": verdict == "PASS",
        "bertscore_f1": bert["mean_f1"],
    }


def evaluate_batch(pipeline_answers, ground_truth):
    references = [row.get("correct_answer", "") for row in ground_truth]
    questions = [row.get("question", row.get("query", "")) for row in ground_truth]
    metrics = {}

    for pipeline_name, answers in pipeline_answers.items():
        rows = [
            {
                "question": question,
                "correct_answer": reference,
                "system_answer": answer,
            }
            for question, reference, answer in zip(questions, references, answers)
        ]
        verdicts = judge_answers(rows)
        pass_fail = [verdict == "PASS" for verdict in verdicts if verdict != "SKIP"]
        bert = compute_bertscore(answers, references)

        metrics[pipeline_name] = {
            "llm_judge_pass_rate": (
                sum(pass_fail) / len(pass_fail) if pass_fail else None
            ),
            "llm_judge_verdicts": verdicts,
            "bertscore_f1": bert["mean_f1"],
            "bertscore_status": bert["status"],
            "bertscore_error": bert["error"],
        }

    return metrics
