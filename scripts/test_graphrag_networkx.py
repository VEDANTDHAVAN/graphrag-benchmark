import json

from pipelines.graphrag.graphrag_pipeline import run_graphrag


def main():
    query = "What does RAG-HAT do for hallucination in RAG?"
    result = run_graphrag(query)
    print(json.dumps(result["details"], indent=2))
    print("\nanswer:\n")
    print(result["answer"])


if __name__ == "__main__":
    main()

