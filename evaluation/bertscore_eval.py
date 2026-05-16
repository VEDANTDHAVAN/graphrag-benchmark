def compute_bertscore(predictions, references, lang="en"):
    pairs = [
        (prediction or "", reference or "")
        for prediction, reference in zip(predictions, references)
        if reference
    ]
    if not pairs:
        return {
            "f1": [],
            "mean_f1": None,
            "status": "SKIP",
            "error": "No reference answers supplied.",
        }

    try:
        import evaluate
    except ImportError:
        return {
            "f1": [],
            "mean_f1": None,
            "status": "SKIP",
            "error": "Install the evaluate package to compute BERTScore.",
        }

    filtered_predictions = [prediction for prediction, _ in pairs]
    filtered_references = [reference for _, reference in pairs]
    try:
        bertscore = evaluate.load("bertscore")
        result = bertscore.compute(
            predictions=filtered_predictions,
            references=filtered_references,
            lang=lang,
            rescale_with_baseline=True,
        )
    except Exception as exc:
        return {
            "f1": [],
            "mean_f1": None,
            "status": "SKIP",
            "error": str(exc),
        }

    f1 = result.get("f1", [])
    return {
        "f1": f1,
        "mean_f1": sum(f1) / len(f1) if f1 else None,
        "status": "OK",
        "error": None,
    }
