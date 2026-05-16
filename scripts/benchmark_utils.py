import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RAW_DATASET_PATH = ROOT / "data" / "raw" / "scientific_papers_2m.jsonl"
RAW_METADATA_PATH = ROOT / "data" / "raw" / "scientific_papers_2m_metadata.json"
EVAL_QUESTIONS_PATH = ROOT / "data" / "eval" / "scientific_eval_questions.json"
BENCHMARK_RESULTS_PATH = ROOT / "data" / "results" / "scientific_benchmark_results.json"
ACCURACY_REPORT_PATH = ROOT / "data" / "results" / "scientific_accuracy_report.json"
FINAL_SUMMARY_PATH = ROOT / "data" / "results" / "final_summary.json"

PIPELINES = ("llm_only", "basic_rag", "graphrag")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, fallback: Any) -> Any:
    try:
        if not path.exists():
            return fallback
        content = path.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else fallback
    except json.JSONDecodeError:
        return fallback


def write_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def token_counter():
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return lambda text: len(enc.encode(text or ""))
    except Exception:
        return lambda text: max(1, len((text or "").split()))


def combined_doc_text(doc: Dict[str, Any]) -> str:
    parts = [
        doc.get("title", ""),
        doc.get("abstract", ""),
        doc.get("article", ""),
    ]
    return "\n\n".join(part for part in parts if part)


def normalize_sections(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    if isinstance(value, str):
        return [v.strip() for v in re.split(r"\n|/n|\\n|;", value) if v.strip()]
    return []


def safe_doc_id(index: int, row: Dict[str, Any]) -> str:
    existing = row.get("doc_id") or row.get("paper_id") or row.get("id")
    if existing:
        return str(existing)
    return f"arxiv_{index:05d}"


def estimate_cost(tokens: int, cost_per_1k: float | None = None) -> float:
    rate = cost_per_1k
    if rate is None:
        rate = float(os.getenv("BENCHMARK_COST_PER_1K", "0.002"))
    return (tokens / 1000) * rate


def words(text: str) -> List[str]:
    return re.findall(r"\b[A-Za-z][A-Za-z0-9-]{2,}\b", text or "")


def first_sentence(text: str, max_chars: int = 360) -> str:
    cleaned = " ".join((text or "").split())
    if not cleaned:
        return ""
    pieces = re.split(r"(?<=[.!?])\s+", cleaned)
    sentence = pieces[0] if pieces else cleaned
    return sentence[:max_chars].rstrip()


def top_terms(text: str, limit: int = 5) -> List[str]:
    stop = {
        "the",
        "and",
        "for",
        "that",
        "with",
        "this",
        "from",
        "are",
        "was",
        "were",
        "paper",
        "using",
        "method",
        "results",
        "show",
    }
    counts: Dict[str, int] = {}
    for term in words(text.lower()):
        if len(term) < 4 or term in stop:
            continue
        counts[term] = counts.get(term, 0) + 1
    return [term for term, _ in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:limit]]
