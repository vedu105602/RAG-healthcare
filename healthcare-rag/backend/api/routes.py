import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from services.ingestion import ingest_document, ingest_url
from services.rag import RAGPipeline

router = APIRouter()
rag_pipeline = RAGPipeline()

# Ensure temp directory exists for file uploads
UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    query: str

class URLRequest(BaseModel):
    url: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence_score: float


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save uploaded file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process and ingest
        num_chunks = ingest_document(file_path, rag_pipeline.vector_store)
        return {"message": f"Successfully processed {file.filename}", "chunks_added": num_chunks}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/upload-url")
async def upload_url(request: URLRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="No URL provided")
        
    try:
        # Process and ingest URL
        num_chunks = ingest_url(request.url, rag_pipeline.vector_store)
        return {"message": f"Successfully processed {request.url}", "chunks_added": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    try:
        response_data = rag_pipeline.generate_response(request.query)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
