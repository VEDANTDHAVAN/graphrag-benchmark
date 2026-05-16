from typing import Dict, List

_ENCODER = None


def _get_encoder():
    global _ENCODER
    if _ENCODER is not None:
        return _ENCODER
    try:
        import tiktoken

        _ENCODER = tiktoken.get_encoding("cl100k_base")
    except Exception:
        _ENCODER = False
    return _ENCODER


def count_tokens(text: str) -> int:
    if not text:
        return 0
    encoder = _get_encoder()
    if encoder:
        return len(encoder.encode(text))
    return max(1, len(text.split()))


def select_under_budget(chunks: List[Dict], token_budget: int) -> List[Dict]:
    selected: List[Dict] = []
    used = 0

    for chunk in chunks:
        text = chunk.get("text", "")
        tokens = count_tokens(text)
        if selected and used + tokens > token_budget:
            continue
        if not selected and tokens > token_budget:
            truncated = " ".join(text.split()[: max(1, token_budget)])
            item = dict(chunk)
            item["text"] = truncated
            item["token_count"] = count_tokens(truncated)
            selected.append(item)
            break
        item = dict(chunk)
        item["token_count"] = tokens
        selected.append(item)
        used += tokens

    return selected
