from benchmark_utils import (
    ACCURACY_REPORT_PATH,
    BENCHMARK_RESULTS_PATH,
    FINAL_SUMMARY_PATH,
    PIPELINES,
    read_json,
    write_json,
)


def main() -> None:
    benchmark_rows = read_json(BENCHMARK_RESULTS_PATH, [])
    accuracy = read_json(ACCURACY_REPORT_PATH, {})
    if not benchmark_rows:
        raise FileNotFoundError(f"No benchmark results found in {BENCHMARK_RESULTS_PATH}")

    summary = {}
    for pipeline in PIPELINES:
        metrics = [row["pipelines"].get(pipeline, {}) for row in benchmark_rows]
        summary[pipeline] = {
            "avg_total_tokens": average(metrics, "total_tokens"),
            "avg_latency_seconds": average(metrics, "latency_seconds"),
            "avg_estimated_cost": average(metrics, "estimated_cost"),
            "llm_judge_pass_rate": accuracy.get(pipeline, {}).get("llm_judge_pass_rate"),
            "bertscore_f1": accuracy.get(pipeline, {}).get("bertscore_f1"),
        }

    baseline = summary.get("llm_only", {})
    for pipeline, item in summary.items():
        item["token_reduction_vs_llm_only"] = reduction(
            baseline.get("avg_total_tokens"), item.get("avg_total_tokens")
        )
        item["latency_reduction_vs_llm_only"] = reduction(
            baseline.get("avg_latency_seconds"), item.get("avg_latency_seconds")
        )
        item["cost_reduction_vs_llm_only"] = reduction(
            baseline.get("avg_estimated_cost"), item.get("avg_estimated_cost")
        )

    write_json(FINAL_SUMMARY_PATH, summary)
    print(f"Saved final summary to {FINAL_SUMMARY_PATH}")


def average(rows, key):
    values = [row.get(key) for row in rows if isinstance(row.get(key), (int, float))]
    return sum(values) / len(values) if values else None


def reduction(baseline, current):
    if not baseline or current is None:
        return None
    return ((baseline - current) / baseline) * 100


if __name__ == "__main__":
    main()
