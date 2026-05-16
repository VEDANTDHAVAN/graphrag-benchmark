import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

FINAL_SUMMARY_PATH = Path("data/results/final_summary.json")


@router.get("/metrics/final-summary")
def final_summary():
    if not FINAL_SUMMARY_PATH.exists():
        return {"status": "missing", "summary": {}}

    try:
        return {
            "status": "ok",
            "summary": json.loads(FINAL_SUMMARY_PATH.read_text(encoding="utf-8")),
        }
    except json.JSONDecodeError:
        return {"status": "error", "summary": {}, "error": "Invalid final_summary.json"}
