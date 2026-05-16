# Deployment

## Recommended Free Deployment: Vercel + Hugging Face Spaces

Render's free and low-cost 512 MB tiers are too small for live pipeline queries because the backend loads ChromaDB, sentence-transformers/PyTorch, and the NetworkX graph. For a no-cost live demo, use:

```text
Frontend: Vercel
Backend: Hugging Face Spaces Docker, CPU Basic
GraphRAG: NetworkX inside the backend process
Vector store: embedded ChromaDB files bundled with the Space
TigerGraph: disabled by default
```

Hugging Face Spaces CPU Basic is the preferred free backend target for this project because it provides substantially more memory than 512 MB PaaS instances.

## Architecture

```text
Frontend (Vercel)
  -> Backend API (Hugging Face Spaces, Render paid tier, or VPS)
  -> NetworkX GraphRAG engine inside the backend process
  -> Embedded ChromaDB persisted on disk
  -> Optional TigerGraph connector, disabled by default
```

NetworkX is the canonical GraphRAG engine for this benchmark. TigerGraph is an optional enterprise connector for larger operational deployments, not a requirement for local development, evaluation, dashboard use, or judging.

## Frontend on Vercel

1. Import `frontend/` as the Vercel project root.
2. Set the public API URL:

```text
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

For Hugging Face Spaces:

```text
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-YOUR_SPACE.hf.space
```

Do not add TigerGraph credentials or private backend secrets to Vercel. The frontend only needs public-safe variables prefixed with `NEXT_PUBLIC_`.

## Backend on Hugging Face Spaces

This is the recommended free backend deployment.

Build the Space bundle:

```sh
python scripts/prepare_hf_space.py
```

Create a new Hugging Face Space:

1. Choose **Docker** as the SDK.
2. Upload the contents of `dist/hf-space`.
3. Add secrets:

```text
ENV=production
OPENAI_API_KEY
HF_TOKEN
FRONTEND_URL=https://your-frontend.vercel.app
BACKEND_URL=https://your-username-your-space.hf.space
ADMIN_API_KEY
SESSION_SECRET
TIGERGRAPH_ENABLED=false
```

4. Test:

```text
https://your-username-your-space.hf.space/health
https://your-username-your-space.hf.space/ready
```

Hugging Face Spaces free storage is not a database. Bundle the generated ChromaDB, graph, and result artifacts with the Space for a reproducible demo. Do not upload `.env` files.

## Backend on Render

Use Render only if you choose a paid instance with enough memory. The 512 MB tiers are not recommended for live pipeline queries.

Use the root `render.yaml`.

Set these secrets in the Render dashboard:

```text
OPENAI_API_KEY
HF_TOKEN
FRONTEND_URL=https://your-frontend.vercel.app
BACKEND_URL=https://your-backend.onrender.com
ADMIN_API_KEY
SESSION_SECRET
```

The Render disk is mounted at `/data` for ChromaDB, uploads, graph artifacts, raw data, and benchmark results.

Health checks:

```text
GET /health
GET /ready
```

`/health` is a lightweight process check. `/ready` validates writable storage, production env configuration, NetworkX readiness, and TigerGraph only when `TIGERGRAPH_ENABLED=true`.

## Docker Compose Production

NetworkX-only deployment:

```sh
cp .env.production.example .env.production
# edit .env.production
docker compose -f docker-compose.prod.yml up -d
```

This starts backend, frontend, and nginx. TigerGraph is not started.

Optional TigerGraph profile:

```sh
docker compose -f docker-compose.prod.yml --profile tigergraph up -d
```

Set `TIGERGRAPH_ENABLED=true` and the `TIGERGRAPH_*` variables only when using this profile.

## Optional VPS Deployment with TigerGraph

TigerGraph can be used for enterprise-scale graph storage, but the benchmark does not depend on it. If enabled:

1. Change all default TigerGraph passwords.
2. Set `TIGERGRAPH_ENABLED=true`.
3. Set `TIGERGRAPH_HOST`, `TIGERGRAPH_GRAPH`, `TIGERGRAPH_USERNAME`, and `TIGERGRAPH_PASSWORD`.
4. Run the compose stack with `--profile tigergraph`.

## Environment Variables

Required for production:

```text
OPENAI_API_KEY
HF_TOKEN
FRONTEND_URL
BACKEND_URL
ADMIN_API_KEY
SESSION_SECRET or JWT_SECRET
```

Optional:

```text
TIGERGRAPH_ENABLED=false
TIGERGRAPH_HOST
TIGERGRAPH_GRAPH
TIGERGRAPH_USERNAME
TIGERGRAPH_PASSWORD
CHROMA_HOST
CHROMA_PORT
```

## Validation

After deployment:

```sh
python scripts/validate_deployment.py
```

For a deployed backend:

```sh
BACKEND_URL=https://your-backend.onrender.com python scripts/validate_deployment.py
```

## Common Issues

- Dashboard shows no final summary: run `python scripts/build_final_summary.py` and restart the backend.
- `/ready` says graph artifact missing: rebuild indexes with `python scripts/rebuild_indexes_from_2m_dataset.py`.
- Upload returns 401/403 in production: include `Authorization: Bearer <ADMIN_API_KEY>` for admin routes.
- Vercel calls localhost: set `NEXT_PUBLIC_API_URL` to the deployed backend URL.
- TigerGraph errors: keep `TIGERGRAPH_ENABLED=false` unless intentionally using the optional connector.
