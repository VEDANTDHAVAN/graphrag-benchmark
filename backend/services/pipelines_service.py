from importlib import import_module
from typing import Callable, Dict


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
    return {
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
