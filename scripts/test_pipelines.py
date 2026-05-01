from pipelines.llm_only.llm_pipeline import run_llm_only
from pipelines.basic_rag.rag_pipeline import run_basic_rag
from pipelines.graphrag.graphrag_pipeline import run_graphrag

query = "Is Company A linked to fraud?"

print("\n--- LLM ONLY ---")
print(run_llm_only(query))

print("\n--- BASIC RAG ---")
print(run_basic_rag(query))

print("\n--- GRAPH RAG ---")
print(run_graphrag(query))
