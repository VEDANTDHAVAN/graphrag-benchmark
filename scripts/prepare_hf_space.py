import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "hf-space"

CODE_DIRS = [
    "backend",
    "evaluation",
    "ingestion",
    "pipelines",
    "scripts",
    "utils",
]

DATA_DIRS = [
    "data/chroma",
    "data/graph",
    "data/results",
    "data/eval",
]


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for name in CODE_DIRS:
        copy_tree(ROOT / name, OUT / name)

    for name in DATA_DIRS:
        source = ROOT / name
        if source.exists():
            copy_tree(source, OUT / name)

    shutil.copy2(ROOT / "requirements.txt", OUT / "requirements.txt")
    shutil.copy2(ROOT / "deploy" / "huggingface" / "Dockerfile", OUT / "Dockerfile")
    shutil.copy2(ROOT / "deploy" / "huggingface" / "README.md", OUT / "README.md")

    (OUT / "data" / "uploads").mkdir(parents=True, exist_ok=True)
    print(f"Hugging Face Space bundle written to {OUT}")


def copy_tree(source: Path, target: Path) -> None:
    ignore = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        ".env",
        ".env.*",
        "*.log",
    )
    shutil.copytree(source, target, ignore=ignore)


if __name__ == "__main__":
    main()
