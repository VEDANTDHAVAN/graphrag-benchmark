import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.services.ingestion_service import ingest_document


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_ingestion.py <path-to-pdf>")
        raise SystemExit(2)

    pdf_path = Path(sys.argv[1])
    data = pdf_path.read_bytes()

    result = __import__("asyncio").run(ingest_document(pdf_path.name, data))
    print(result)


if __name__ == "__main__":
    main()
