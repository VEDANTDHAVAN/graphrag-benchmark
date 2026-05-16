import json

from pipelines.graphrag.graphrag_pipeline import run_graphrag


def main():
    query = "What is the main contribution or focus of the paper about laser beams propagating through turbulent atmospheres?
"
    result = run_graphrag(query)
    print(json.dumps(result["details"], indent=2))
    print("\nanswer:\n")
    print(result["answer"])


if __name__ == "__main__":
    main()

