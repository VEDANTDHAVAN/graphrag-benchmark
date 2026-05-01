from fastapi import FastAPI
from pipelines.llm_only.llm_pipeline import run_llm_only
from pipelines.basic_rag.rag_pipeline import run_basic_rag
from pipelines.graphrag.graphrag_pipeline import run_graphrag

app = FastAPI()

@app.post("/query")
def query_all(data: dict):
    query = data["query"]

    return {
        "query": query,
        "llm_only": run_llm_only(query),
        "basic_rag": run_basic_rag(query, vector_store=None),
        "graphrag": run_graphrag(query)
    }
