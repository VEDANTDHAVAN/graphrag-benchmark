from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.security import AdminDependency

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), _: None = AdminDependency):
    allowed = (".pdf", ".txt", ".csv")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, CSV supported")

    content = await file.read()

    from backend.services.ingestion_service import ingest_document

    try:
        result = await ingest_document(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "stage": "ingestion",
                "message": "Ingestion failed",
            },
        ) from exc

    return {
        "status": result.get("status", "success"),
        "data": result,
    }
