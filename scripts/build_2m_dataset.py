from benchmark_utils import (
    RAW_DATASET_PATH,
    RAW_METADATA_PATH,
    combined_doc_text,
    normalize_sections,
    safe_doc_id,
    token_counter,
    write_json,
    write_jsonl,
)

DATASET_NAME = "armanc/scientific_papers"
DATASET_CONFIG = "arxiv"
TARGET_TOKENS = 2_000_000


def main() -> None:
    count_tokens = token_counter()
    dataset = load_arxiv_train_stream()

    rows = []
    total_tokens = 0

    for index, row in enumerate(dataset):
        article = row.get("article", "")
        abstract = row.get("abstract", "")
        title = row.get("title") or first_title(article, index)
        token_count = count_tokens(combined_doc_text({"title": title, "abstract": abstract, "article": article}))

        if token_count <= 0:
            continue

        total_tokens += token_count
        rows.append(
            {
                "doc_id": safe_doc_id(index, row),
                "title": title,
                "article": article,
                "abstract": abstract,
                "section_names": normalize_sections(row.get("section_names") or row.get("sections")),
                "token_count": token_count,
                "cumulative_tokens": total_tokens,
                "source": f"{DATASET_NAME}/{DATASET_CONFIG}",
            }
        )

        if total_tokens >= TARGET_TOKENS:
            break

    write_jsonl(RAW_DATASET_PATH, rows)
    write_json(
        RAW_METADATA_PATH,
        {
            "num_documents": len(rows),
            "total_tokens": total_tokens,
            "average_tokens_per_document": total_tokens / len(rows) if rows else 0,
            "dataset_name": DATASET_NAME,
            "dataset_config": DATASET_CONFIG,
        },
    )
    print(f"Saved {len(rows)} documents and {total_tokens:,} tokens to {RAW_DATASET_PATH}")


def first_title(article: str, index: int) -> str:
    first_line = next((line.strip() for line in (article or "").splitlines() if line.strip()), "")
    return first_line[:140] if first_line else f"Scientific paper {index + 1}"


def load_arxiv_train_stream():
    """
    Newer versions of `datasets` no longer execute legacy dataset scripts.
    armanc/scientific_papers is script-based on `main`, so load the Parquet
    shards committed under the dataset repo's arxiv/ folder instead.
    """
    import os
    from datasets import load_dataset
    from huggingface_hub import HfApi, hf_hub_url

    token = os.getenv("HF_TOKEN")
    api = HfApi(token=token)
    train_files = []
    revision = None

    for candidate_revision in ("refs/convert/parquet", "main"):
        files = api.list_repo_files(
            repo_id=DATASET_NAME,
            repo_type="dataset",
            revision=candidate_revision,
        )
        train_files = sorted(
            path
            for path in files
            if path.startswith(f"{DATASET_CONFIG}/")
            and path.endswith(".parquet")
            and ("/train/" in path or "/partial-train/" in path or "train" in path)
        )
        if train_files:
            revision = candidate_revision
            break

    if not train_files:
        raise RuntimeError(
            f"No {DATASET_CONFIG} train or partial-train Parquet files found in {DATASET_NAME}."
        )

    parquet_urls = [
        hf_hub_url(
            repo_id=DATASET_NAME,
            filename=path,
            repo_type="dataset",
            revision=revision,
        )
        for path in train_files
    ]

    return load_dataset(
        "parquet",
        data_files=parquet_urls,
        split="train",
        streaming=True,
    )


if __name__ == "__main__":
    main()
