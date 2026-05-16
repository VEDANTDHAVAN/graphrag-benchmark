## GraphRAG Benchmark (Hackathon)

Local benchmark harness to compare three pipelines side-by-side:

- LLM-only
- Basic RAG (ChromaDB)
- GraphRAG (NetworkX)

### Why NetworkX is the Primary GraphRAG Engine

The goal of this project is methodological benchmarking: prove whether graph-structured retrieval and multi-hop reasoning improve efficiency and answer quality compared with LLM-only and Basic RAG.

GraphRAG is defined here by the retrieval method, not by dependence on a specific graph database vendor. NetworkX provides the graph traversal and reasoning capabilities needed for the benchmark while staying lightweight, deterministic, and reproducible on any laptop.

TigerGraph remains supported as an optional enterprise connector for large-scale production use, but it is not required for local development, ingestion, benchmarking, evaluation, dashboard functionality, or judging. In practice, TigerGraph setup introduced operational complexity such as authentication issues, Docker resource requirements, and infrastructure overhead that distracted from the benchmark objective.

To keep judging easy and reproducible, NetworkX is the default implementation.

| Capability | NetworkX | TigerGraph |
|----------|----------|----------|
| Multi-hop graph traversal | Yes | Yes |
| GraphRAG benchmarking | Yes | Yes |
| Runs on any laptop | Yes | No |
| Zero setup overhead | Yes | No |
| Infrastructure complexity | Low | High |
| Required for benchmark | Yes | No |
| Enterprise scalability | Limited | Excellent |

The benchmark conclusions are based on retrieval methodology, not on dependence on a specific graph database.

### Local Development

Backend (FastAPI):

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend (Next.js):

```powershell
cd frontend
copy .env.example .env.local
# edit NEXT_PUBLIC_API_URL if needed
npm.cmd install
npm.cmd run dev
```

Open:

- Frontend: `http://localhost:3005`
- Backend health: `http://127.0.0.1:8000/health`

### Deployment Target

- Frontend on Vercel
- Backend on Render (Docker), running NetworkX GraphRAG by default
- Persistent disk mounted at `/data` for:
  - ChromaDB: `/data/chroma`
  - Graph: `/data/graph/graphrag_graph.pkl`
  - Uploads: `/data/uploads`
- TigerGraph is optional and disabled by default.

### Render Deployment (Backend)

1. Push this repo to GitHub.
2. In Render, create a new service from repo using the blueprint (`render.yaml`), or create a Docker web service manually pointing at `backend/Dockerfile`.
3. Ensure a persistent disk is attached at `/data`.
4. Set env vars (Render):
   - `CHROMA_PATH=/data/chroma`
   - `GRAPH_PATH=/data/graph/graphrag_graph.pkl`
   - `UPLOAD_DIR=/data/uploads`
   - `CORS_ORIGINS=https://YOUR-VERCEL-DOMAIN.vercel.app` (set after Vercel deploy)

Verify:

- `GET https://YOUR-RENDER-URL/health` returns `{"status":"ok"}`
- `GET https://YOUR-RENDER-URL/ready` returns readiness checks for storage, NetworkX artifacts, and optional TigerGraph configuration.

### Vercel Deployment (Frontend)

1. Import `frontend/` as the Vercel project root.
2. Set env var:
   - `NEXT_PUBLIC_API_URL=https://YOUR-RENDER-URL`
3. Deploy.

### Notes

- Local development continues to use repo-relative defaults under `data/`.
- In production, set `CHROMA_PATH`, `GRAPH_PATH`, and `UPLOAD_DIR` to point at `/data/...`.

### Accuracy Evaluation

Create `evaluation/ground_truth.json` with 30-50 reference answers:

```json
[
  {
    "question": "What does RAG-HAT do for hallucination in RAG?",
    "correct_answer": "RAG-HAT detects and reduces hallucinated answers by checking generated responses against retrieved evidence."
  }
]
```

Use the same questions in `experiments/queries.json`:

```json
[
  { "query": "What does RAG-HAT do for hallucination in RAG?" }
]
```

Then run:

```powershell
$env:HF_TOKEN="your_huggingface_token"
python experiments/run_benchmark.py
```

The script writes `experiments/results/combined_results.json` with LLM-as-a-judge pass rate and rescaled BERTScore F1 for each pipeline. To show per-query accuracy in the dashboard for questions that exist in `ground_truth.json`, set `ENABLE_LIVE_ACCURACY=true` before starting the backend.

### 2 Million Token Benchmark and Accuracy Evaluation

Run the full scientific-papers benchmark workflow:

```powershell
python scripts/build_2m_dataset.py
python scripts/rebuild_indexes_from_2m_dataset.py
python scripts/generate_eval_questions.py
python scripts/run_full_benchmark.py
$env:HF_TOKEN="your_huggingface_token"
python scripts/evaluate_accuracy.py
python scripts/build_final_summary.py
```

This uses `armanc/scientific_papers` with the `arxiv` configuration, selects roughly 2,000,000 `cl100k_base` tokens, rebuilds ChromaDB and the NetworkX graph, generates 40 grounded evaluation questions, runs LLM-only, Basic RAG, and GraphRAG, and writes:

- `data/raw/scientific_papers_2m.jsonl`
- `data/raw/scientific_papers_2m_metadata.json`
- `data/eval/scientific_eval_questions.json`
- `data/results/scientific_benchmark_results.json`
- `data/results/scientific_accuracy_report.json`
- `data/results/final_summary.json`

The benchmark dashboard reads `final_summary.json` through the backend and displays LLM judge pass rate, BERTScore F1, token reduction, latency reduction, cost reduction, and winner badges.

### Production Deployment

See `DEPLOYMENT.md` for Vercel, Render, Docker Compose, optional TigerGraph, health checks, and environment-variable setup.

NetworkX-only deployment is the recommended default:

```powershell
copy .env.production.example .env.production
docker compose -f docker-compose.prod.yml up -d
```

Optional TigerGraph deployment:

```powershell
docker compose -f docker-compose.prod.yml --profile tigergraph up -d
```

Use TigerGraph only when you explicitly want the optional enterprise connector.
