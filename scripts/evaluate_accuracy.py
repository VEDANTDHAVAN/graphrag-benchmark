from benchmark_utils import (
    ACCURACY_REPORT_PATH,
    BENCHMARK_RESULTS_PATH,
    PIPELINES,
    read_json,
    write_json,
)
from evaluation.bertscore_eval import compute_bertscore
from evaluation.llm_judge import judge_answers


def main() -> None:
    rows = read_json(BENCHMARK_RESULTS_PATH, [])
    if not rows:
        raise FileNotFoundError(f"No benchmark results found in {BENCHMARK_RESULTS_PATH}")

    report = {}
    for pipeline in PIPELINES:
        answers = [row["pipelines"].get(pipeline, {}).get("answer", "") for row in rows]
        references = [row.get("correct_answer", "") for row in rows]
        judge_rows = [
            {
                "question": row.get("question", ""),
                "correct_answer": row.get("correct_answer", ""),
                "system_answer": row["pipelines"].get(pipeline, {}).get("answer", ""),
            }
            for row in rows
        ]
        verdicts = judge_answers(judge_rows)
        judged = [verdict for verdict in verdicts if verdict != "SKIP"]
        bert = compute_bertscore(answers, references)

        report[pipeline] = {
            "llm_judge_pass_rate": (
                sum(verdict == "PASS" for verdict in judged) / len(judged) if judged else None
            ),
            "bertscore_f1": bert["mean_f1"],
            "num_questions": len(rows),
        }

    write_json(ACCURACY_REPORT_PATH, report)
    print(f"Saved accuracy report to {ACCURACY_REPORT_PATH}")


if __name__ == "__main__":
    main()
