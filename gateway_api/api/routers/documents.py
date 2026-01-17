from fastapi import APIRouter, UploadFile, File, HTTPException, status
import httpx
from core.config import settings

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)):
    """
    Proxy endpoint: Receives a file and forwards it to the Ingestion Service (Microservice 3).
    Microservice 3 is responsible for parsing and vectorizing the PDF.
    """
    ingestion_service_url = f"{settings.VECTOR_DB_URL.replace('/search', '')}/upload" 
    # Note: settings.VECTOR_DB_URL defaults to "http://ingestion-service:8002" (base) or we assumed it enters /search?
    # In config.py: VECTOR_DB_URL: str = "http://ingestion-service:8002"
    
    # We'll construct the URL.
    upload_url = f"{settings.VECTOR_DB_URL}/upload"

    try:
        async with httpx.AsyncClient() as client:
            # Stream the file to the other service
            files = {'file': (file.filename, file.file, file.content_type)}
            response = await client.post(upload_url, files=files, timeout=30.0)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Ingestion Service failed: {response.text}"
                )
            
            return response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ingestion Service unreachable: {str(exc)}"
        )
