import networkx as nx

from pipelines.graphrag import hybrid_retriever as hybrid_module
from pipelines.graphrag.hybrid_retriever import HybridGraphRetriever

QUERY = "How do variable stars help determine distance and star formation history in nearby dwarf galaxies?"


class FakeVectorStore:
    def search(self, query, k=8, filters=None):
        return [
            {
                "chunk_id": "variable_stars_chunk_0000",
                "doc_id": "variable_stars_doc",
                "text": (
                    "A magnitude limited complete census of variable stars in nearby dwarf "
                    "galaxies allows important contributions to distance determinations and "
                    "the star formation history of these systems."
                ),
            },
            {
                "chunk_id": "jacobi_chunk_0000",
                "doc_id": "unrelated_doc",
                "text": "The exact solution of the Jacobi equation is used as the unperturbed solution.",
            },
        ]


def lexical_rerank(query, chunks, embedding_model=None):
    terms = [
        "variable stars",
        "nearby dwarf galaxies",
        "distance determinations",
        "star formation history",
        "tracers of star formation",
    ]
    ranked = []
    for chunk in chunks:
        text = chunk.get("text", "").lower()
        item = dict(chunk)
        item["score"] = sum(1 for term in terms if term in text) / len(terms)
        item.setdefault("source", "graph_expansion")
        item.setdefault("graph_distance", 1)
        ranked.append(item)
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def build_graph():
    graph = nx.MultiDiGraph()
    graph.add_node(
        "chunk:variable_stars_chunk_0000",
        kind="chunk",
        chunk_id="variable_stars_chunk_0000",
        doc_id="variable_stars_doc",
        text=FakeVectorStore().search(QUERY)[0]["text"],
    )
    graph.add_node(
        "chunk:variable_stars_chunk_0001",
        kind="chunk",
        chunk_id="variable_stars_chunk_0001",
        doc_id="variable_stars_doc",
        text=(
            "Different classes of variables function as tracers of star formation during "
            "different epochs and improve understanding of nearby dwarf galaxies."
        ),
    )
    graph.add_node(
        "chunk:jacobi_chunk_0000",
        kind="chunk",
        chunk_id="jacobi_chunk_0000",
        doc_id="unrelated_doc",
        text="The exact solution of the Jacobi equation is used as the unperturbed solution.",
    )
    graph.add_node("entity:variable_stars", kind="entity", entity_id="variable_stars", label="variable stars")
    graph.add_node("entity:jacobi", kind="entity", entity_id="jacobi", label="jacobi")
    graph.add_edge("chunk:variable_stars_chunk_0000", "entity:variable_stars", kind="MENTIONS")
    graph.add_edge("chunk:variable_stars_chunk_0001", "entity:variable_stars", kind="MENTIONS")
    graph.add_edge("chunk:jacobi_chunk_0000", "entity:jacobi", kind="MENTIONS")
    return graph


def test_hybrid_retriever_keeps_variable_stars_context(monkeypatch):
    monkeypatch.setattr(hybrid_module, "rerank_chunks", lexical_rerank)
    retriever = HybridGraphRetriever(
        vector_store=FakeVectorStore(),
        graph=build_graph(),
        top_k_seed=2,
        graph_hops=1,
        final_top_k=2,
        min_similarity_threshold=0.25,
        token_budget=300,
    )

    result = retriever.retrieve(QUERY)
    selected_text = " ".join(chunk["text"].lower() for chunk in result["selected_contexts"])

    assert "variable stars" in selected_text
    assert "nearby dwarf galaxies" in selected_text
    assert "distance determinations" in selected_text
    assert "star formation history" in selected_text
    assert "tracers of star formation" in selected_text
    assert "jacobi equation" not in selected_text
    assert result["retrieval_trace"]["mode"] == "hybrid_graphrag"
    assert result["retrieval_trace"]["reranked_candidate_count"] >= 2
    assert result["fallback_used"] in {True, False}


def test_graphrag_pipeline_generates_answer_with_trace(monkeypatch):
    from pipelines.graphrag import graphrag_pipeline

    retrieval = {
        "selected_contexts": [
            {
                "chunk_id": "variable_stars_chunk_0000",
                "doc_id": "variable_stars_doc",
                "text": FakeVectorStore().search(QUERY)[0]["text"],
                "score": 0.9,
                "source": "seed",
                "graph_distance": 0,
            }
        ],
        "seed_chunks": [],
        "expanded_nodes": [],
        "expanded_edges": [],
        "reranked_candidates": [],
        "fallback_used": False,
        "retrieval_trace": {
            "mode": "hybrid_graphrag",
            "seed_count": 1,
            "expanded_node_count": 1,
            "expanded_edge_count": 1,
            "reranked_candidate_count": 1,
            "fallback_used": False,
            "graph_hops": 1,
        },
        "connected_entities": [{"label": "variable stars"}],
    }

    class FakeRetriever:
        def retrieve(self, query):
            return retrieval

    monkeypatch.setattr(graphrag_pipeline, "get_hybrid_retriever", lambda: FakeRetriever())
    monkeypatch.setattr(
        graphrag_pipeline,
        "generate",
        lambda prompt: {
            "text": "Variable stars provide distance determinations and trace star formation history.",
            "total_tokens": 42,
            "latency": 0.01,
            "prompt_tokens": 30,
            "completion_tokens": 12,
        },
    )

    response = graphrag_pipeline.run_graphrag(QUERY)

    assert response["status"] == "success"
    assert response["answer"]
    assert response["retrieval_trace"]["mode"] == "hybrid_graphrag"
    assert response["details"]["retrieval_trace"]["mode"] == "hybrid_graphrag"
