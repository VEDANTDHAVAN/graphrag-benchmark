from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")

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
                "message": str(exc),
            },
        ) from exc

    return {
        "status": result.get("status", "success"),
        "data": result,
    }
