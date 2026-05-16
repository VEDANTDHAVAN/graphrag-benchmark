import argparse

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
    parser = argparse.ArgumentParser(description="Evaluate benchmark answer accuracy.")
    parser.add_argument(
        "--allow-skip-judge",
        action="store_true",
        help="Write null LLM judge pass rates instead of failing when judge calls are unavailable.",
    )
    parser.add_argument(
        "--skip-bertscore",
        action="store_true",
        help="Reuse existing BERTScore values from scientific_accuracy_report.json instead of recomputing them.",
    )
    args = parser.parse_args()

    rows = read_json(BENCHMARK_RESULTS_PATH, [])
    if not rows:
        raise FileNotFoundError(f"No benchmark results found in {BENCHMARK_RESULTS_PATH}")

    existing_report = read_json(ACCURACY_REPORT_PATH, {})
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
        judge_details = judge_answers(
            judge_rows,
            return_details=True,
            raise_on_error=not args.allow_skip_judge,
        )
        verdicts = [item["verdict"] for item in judge_details]
        judged = [verdict for verdict in verdicts if verdict != "SKIP"]
        skipped = [item for item in judge_details if item["verdict"] == "SKIP"]
        if not judged and not args.allow_skip_judge:
            errors = sorted({item.get("error") or "unknown error" for item in skipped})
            raise RuntimeError(
                "LLM judge produced no verdicts. "
                "Set HF_TOKEN and ensure the judge model is available. "
                f"Errors: {'; '.join(errors)}"
            )

        if args.skip_bertscore:
            bert_f1 = existing_report.get(pipeline, {}).get("bertscore_f1")
        else:
            bert = compute_bertscore(answers, references)
            bert_f1 = bert["mean_f1"]

        report[pipeline] = {
            "llm_judge_pass_rate": (
                sum(verdict == "PASS" for verdict in judged) / len(judged) if judged else None
            ),
            "llm_judge_verdicts": verdicts,
            "llm_judge_judged_count": len(judged),
            "llm_judge_skipped_count": len(skipped),
            "llm_judge_errors": sorted(
                {item.get("error") for item in skipped if item.get("error")}
            ),
            "bertscore_f1": bert_f1,
            "num_questions": len(rows),
        }

    write_json(ACCURACY_REPORT_PATH, report)
    print(f"Saved accuracy report to {ACCURACY_REPORT_PATH}")


if __name__ == "__main__":
    main()
