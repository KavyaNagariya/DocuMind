from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from app.services.rag_service import RAGService
from app.ingest_docs import run_ingestion
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Documind Enterprise v1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
@limiter.limit("5/minute")
async def chat(data: ChatRequest, request: Request):
    async def event_generator():
        async for chunk in rag_service.stream_answer(data.message, data.history):
            if chunk:
                if chunk.startswith("__CITATIONS__"):
                    citations_json = chunk.replace("__CITATIONS__", "")
                    yield f"event: citations\ndata: {citations_json}\n\n"
                else:
                    payload = json.dumps({"token": chunk})
                    yield f"event: token\ndata: {payload}\n\n"

    return StreamingResponse(event_generator(), media_type="text-event-stream")

@app.post("/upload")
@limiter.limit("5/minute")
async def upload_documents(request: Request, files: List[UploadFile] = File(...)):
    uploaded_files = []
    errors = []

    os.makedirs("documents", exist_ok=True)

    
    for file in files:
        if not file.filename.endswith(".pdf"):
            errors.append(f"{file.filename}: Only PDF files are supported.")
            continue
        
        file_path = os.path.join("documents", file.filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Run the ingestion pipeline for the newly uploaded file
            run_ingestion(file_path)
            uploaded_files.append(file.filename)
        except Exception as e:
            errors.append(f"{file.filename}: Ingestion failed: {str(e)}")
            
    if errors and not uploaded_files:
        raise HTTPException(status_code=500, detail={"message": "All uploads failed", "errors": errors})
    
    return {
        "message": f"Successfully processed {len(uploaded_files)} files.",
        "uploaded": uploaded_files,
        "errors": errors
    }
