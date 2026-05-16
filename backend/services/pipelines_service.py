import json
import os
from importlib import import_module
from pathlib import Path
from typing import Callable, Dict


GROUND_TRUTH_PATH = Path("evaluation/ground_truth.json")


def _load_reference_answer(question: str) -> str:
    if not GROUND_TRUTH_PATH.exists():
        return ""

    try:
        data = json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""

    if isinstance(data, dict):
        return data.get(question, "")

    if isinstance(data, list):
        for row in data:
            if not isinstance(row, dict):
                continue
            row_question = row.get("question", row.get("query", ""))
            if row_question == question:
                return row.get("correct_answer", row.get("answer", ""))

    return ""


def _safe_run(name: str, runner: Callable[[str], Dict], question: str) -> Dict:
    try:
        result = runner(question)
        if not isinstance(result, dict):
            return {
                "status": "error",
                "answer": "",
                "error": f"{name} returned {type(result).__name__}, expected dict",
            }

        return {
            "status": "success",
            **result,
        }
    except Exception as exc:
        return {
            "status": "error",
            "answer": "",
            "error": str(exc),
        }


def _run_pipeline(name: str, module_path: str, function_name: str, question: str) -> Dict:
    try:
        module = import_module(module_path)
        runner = getattr(module, function_name)
    except Exception as exc:
        return {
            "status": "error",
            "answer": "",
            "error": f"Failed to load {name}: {exc}",
        }

    return _safe_run(name, runner, question)


def run_all_pipelines(question: str) -> Dict:
    """
    Lazily import pipelines so the API can boot even when optional runtime
    dependencies, model files, or external services are not ready yet.
    """
    response = {
        "query": question,
        "pipelines": {
            "llm_only": _run_pipeline(
                "llm_only",
                "pipelines.llm_only.llm_pipeline",
                "run_llm_only",
                question,
            ),
            "basic_rag": _run_pipeline(
                "basic_rag",
                "pipelines.basic_rag.rag_pipeline",
                "run_basic_rag",
                question,
            ),
            "graphrag": _run_pipeline(
                "graphrag",
                "pipelines.graphrag.graphrag_pipeline",
                "run_graphrag",
                question,
            ),
        },
    }

    if os.getenv("ENABLE_LIVE_ACCURACY", "").lower() in {"1", "true", "yes"}:
        correct_answer = _load_reference_answer(question)
        if correct_answer:
            from evaluation.evaluator import evaluate_single_answer

            for result in response["pipelines"].values():
                if result.get("status") == "success":
                    result["accuracy"] = evaluate_single_answer(
                        question,
                        correct_answer,
                        result.get("answer", ""),
                    )

    return response
