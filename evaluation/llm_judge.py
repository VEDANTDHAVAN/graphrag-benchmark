import os

JUDGE_MODEL = os.getenv("HF_JUDGE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")

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


def judge_answer(system_answer, correct_answer, question="", client=None):
    if not correct_answer:
        return "SKIP"

    if client is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            return "SKIP"

        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            return "SKIP"

        client = InferenceClient(model=JUDGE_MODEL, token=token)

    prompt = JUDGE_PROMPT.format(
        question=question,
        correct_answer=correct_answer,
        system_answer=system_answer or "",
    )
    try:
        response = client.chat_completion(
            [{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0.0,
        )
    except Exception:
        return "SKIP"

    return _verdict_from_text(response.choices[0].message.content)


def judge_answers(rows, model=JUDGE_MODEL):
    token = os.getenv("HF_TOKEN")
    if not token:
        return ["SKIP" for _ in rows]

    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        return ["SKIP" for _ in rows]

    client = InferenceClient(model=model, token=token)
    verdicts = []
    for row in rows:
        verdicts.append(
            judge_answer(
                row.get("system_answer", ""),
                row.get("correct_answer", ""),
                row.get("question", ""),
                client=client,
            )
        )
    return verdicts
