import time

from benchmark_utils import (
    BENCHMARK_RESULTS_PATH,
    EVAL_QUESTIONS_PATH,
    PIPELINES,
    estimate_cost,
    read_json,
    write_json,
)


def main() -> None:
    questions = read_json(EVAL_QUESTIONS_PATH, [])
    if not questions:
        raise FileNotFoundError(f"No evaluation questions found in {EVAL_QUESTIONS_PATH}")

    from pipelines.basic_rag.rag_pipeline import run_basic_rag
    from pipelines.graphrag.graphrag_pipeline import run_graphrag
    from pipelines.llm_only.llm_pipeline import run_llm_only

    runners = {
        "llm_only": run_llm_only,
        "basic_rag": run_basic_rag,
        "graphrag": run_graphrag,
    }
    rows = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        print(f"[{index}/{len(questions)}] {question}")
        pipeline_results = {}
        for name in PIPELINES:
            pipeline_results[name] = normalize_result(runners[name], question)
        rows.append(
            {
                "question": question,
                "correct_answer": item.get("correct_answer", ""),
                "category": item.get("category", ""),
                "difficulty": item.get("difficulty", ""),
                "source_doc_ids": item.get("source_doc_ids", []),
                "pipelines": pipeline_results,
            }
        )

    write_json(BENCHMARK_RESULTS_PATH, rows)
    print(f"Saved benchmark results to {BENCHMARK_RESULTS_PATH}")


def normalize_result(runner, question):
    started = time.time()
    try:
        raw = runner(question)
        status = raw.get("status", "success")
    except Exception as exc:
        elapsed = time.time() - started
        return {
            "status": "error",
            "answer": "",
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_seconds": elapsed,
            "estimated_cost": 0,
            "retrieved_context_count": 0,
            "graph_nodes_used": 0,
            "graph_edges_used": 0,
            "error": str(exc),
        }

    details = raw.get("details") or {}
    total_tokens = raw.get("total_tokens", raw.get("tokens", 0)) or 0
    input_tokens = details.get("prompt_tokens", raw.get("prompt_tokens", 0)) or 0
    output_tokens = details.get("completion_tokens", raw.get("completion_tokens", 0)) or 0
    context_count = len(details.get("retrieved_chunks") or details.get("chunks") or [])
    reasoning_paths = details.get("reasoning_paths") or []
    matched_entities = details.get("matched_entities") or []
    graph_chunks = details.get("chunks") or []
    retrieval_trace = details.get("retrieval_trace") or raw.get("retrieval_trace") or {}

    return {
        "status": status,
        "answer": raw.get("answer", ""),
        "total_tokens": total_tokens,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_seconds": raw.get("latency", time.time() - started) or 0,
        "estimated_cost": estimate_cost(total_tokens),
        "retrieved_context_count": context_count,
        "graph_nodes_used": retrieval_trace.get("expanded_node_count", len(matched_entities) + len(graph_chunks)),
        "graph_edges_used": retrieval_trace.get(
            "expanded_edge_count",
            sum(max(0, len(path) - 1) for path in reasoning_paths),
        ),
        "seed_chunks_used": retrieval_trace.get("seed_count", details.get("seed_chunks_used", 0)),
        "fallback_used": retrieval_trace.get("fallback_used", details.get("fallback_used", False)),
        "reranked_candidate_count": retrieval_trace.get(
            "reranked_candidate_count",
            details.get("reranked_candidate_count", 0),
        ),
    }


if __name__ == "__main__":
    main()
