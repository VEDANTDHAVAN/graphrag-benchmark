import os
import time
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

JUDGE_MODEL = os.getenv("HF_JUDGE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
JUDGE_MAX_RETRIES = int(os.getenv("HF_JUDGE_MAX_RETRIES", "2"))

JUDGE_PROMPT = """Grade the system's answer.
Question: {question}
Correct answer: {correct_answer}
System answer: {system_answer}

Reply with only PASS or FAIL.
PASS = the system answer correctly addresses the question with no major errors.
FAIL = the answer is wrong, missing, or contradicts the correct answer."""


def _verdict_from_text(text):
    normalized = (text or "").strip().upper()
    if normalized.startswith("PASS") or "PASS" in normalized:
        return "PASS"
    return "FAIL"


def judge_answer_result(system_answer, correct_answer, question="", client=None) -> Dict[str, Any]:
    if not correct_answer:
        return {"verdict": "SKIP", "error": "Missing reference answer", "raw": ""}

    if client is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            return {"verdict": "SKIP", "error": "HF_TOKEN is not set", "raw": ""}

        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            return {"verdict": "SKIP", "error": f"huggingface_hub import failed: {exc}", "raw": ""}

        client = InferenceClient(model=JUDGE_MODEL, token=token)

    prompt = JUDGE_PROMPT.format(
        question=question,
        correct_answer=correct_answer,
        system_answer=system_answer or "",
    )
    last_error = None
    for attempt in range(JUDGE_MAX_RETRIES + 1):
        try:
            response = client.chat_completion(
                [{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.0,
            )
            raw = response.choices[0].message.content
            return {"verdict": _verdict_from_text(raw), "error": None, "raw": raw}
        except Exception as exc:
            last_error = exc
            if attempt < JUDGE_MAX_RETRIES:
                time.sleep(1.5 * (attempt + 1))

    return {"verdict": "SKIP", "error": f"Judge request failed: {last_error}", "raw": ""}


def judge_answer(system_answer, correct_answer, question="", client=None):
    return judge_answer_result(system_answer, correct_answer, question, client=client)["verdict"]


def judge_answers(rows, model=JUDGE_MODEL, return_details=False, raise_on_error=False):
    token = os.getenv("HF_TOKEN")
    if not token:
        message = "HF_TOKEN is not set. Set it in the environment or .env before running accuracy evaluation."
        if raise_on_error:
            raise RuntimeError(message)
        skipped = [{"verdict": "SKIP", "error": message, "raw": ""} for _ in rows]
        return skipped if return_details else [item["verdict"] for item in skipped]

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        message = f"huggingface_hub import failed: {exc}"
        if raise_on_error:
            raise RuntimeError(message) from exc
        skipped = [{"verdict": "SKIP", "error": message, "raw": ""} for _ in rows]
        return skipped if return_details else [item["verdict"] for item in skipped]

    client = InferenceClient(model=model, token=token)
    results: List[Dict[str, Any]] = []
    for row in rows:
        result = judge_answer_result(
            row.get("system_answer", ""),
            row.get("correct_answer", ""),
            row.get("question", ""),
            client=client,
        )
        if result["verdict"] == "SKIP" and raise_on_error:
            raise RuntimeError(result["error"] or "Judge request skipped")
        results.append(result)

    return results if return_details else [item["verdict"] for item in results]
