import json
from pipelines.llm_only.llm_pipeline import run_llm_only
from pipelines.basic_rag.rag_pipeline import run_basic_rag
from pipelines.graphrag.graphrag_pipeline import run_graphrag
from evaluation.evaluator import evaluate

def run():
    queries = json.load(open("experiments/queries.json"))
    ground_truth = json.load(open("evaluation/ground_truth.json"))

    results = []

    for q in queries:
        query = q["query"]

        llm = run_llm_only(query)
        rag = run_basic_rag(query, vector_store=None)  # initialize properly
        graph = run_graphrag(query)

        outputs = {
            "llm_only": llm,
            "basic_rag": rag,
            "graphrag": graph
        }

        eval_res = evaluate(query, outputs, ground_truth.get(query, ""))

        results.append({"query": query, "results": eval_res})

    with open("experiments/results/combined_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run()
