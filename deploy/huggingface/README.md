---
title: GraphRAG Benchmark Backend
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Hugging Face Spaces Backend

Use this when Render's 512 MB memory limit is too small for live pipeline queries.

Hugging Face Spaces CPU Basic currently provides enough free memory for this benchmark backend. The Space runs only the FastAPI backend. Keep the frontend on Vercel and set:

```text
NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-YOUR_SPACE.hf.space
```

## Build a Space Bundle

From the repo root:

```powershell
python scripts/prepare_hf_space.py
```

This writes a deployable backend bundle to:

```text
dist/hf-space
```

The bundle includes:

- backend code
- pipeline/evaluation/ingestion code
- requirements
- generated `data/chroma`
- generated `data/graph`
- generated `data/results`
- Hugging Face Dockerfile

It does not include `.env` files or secrets.

## Deploy

1. Create a new Hugging Face Space.
2. Choose **Docker** as the Space SDK.
3. Upload the contents of `dist/hf-space`.
4. Add Space secrets:

```text
OPENAI_API_KEY
HF_TOKEN
FRONTEND_URL=https://your-vercel-app.vercel.app
BACKEND_URL=https://your-username-your-space.hf.space
ADMIN_API_KEY
SESSION_SECRET
TIGERGRAPH_ENABLED=false
ENV=production
```

5. Wait for the Space to build.
6. Test:

```text
https://your-username-your-space.hf.space/health
https://your-username-your-space.hf.space/ready
```

TigerGraph is not required.
