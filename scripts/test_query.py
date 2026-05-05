import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.services.pipelines_service import run_all_pipelines


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Usage: python scripts/test_query.py <query text>")
        raise SystemExit(2)

    result = run_all_pipelines(query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
