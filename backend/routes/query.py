from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.pipelines_service import run_all_pipelines

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)


@router.post("/query")
def query_all(request: QueryRequest):
    question = request.query.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    return run_all_pipelines(question)
