from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from app.services.rag_service import RAGService
from app.ingest_docs import run_ingestion
from pydantic import BaseModel

app = FastAPI(title="Documind Enterprise v1.0")

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
async def chat(request: ChatRequest):
    result = rag_service.answer_question(request.message, request.history)
    docs = result.get("context", [])
    return {
            "answer": result["answer"],
            "citations": [
                {
                    "sources": doc.metadata.get("source"),
                    "page": doc.metadata.get("page"),
                    "snippet": doc.page_content[:200] + "..."
                 }
                for doc in docs
            ] if docs else []
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    os.makedirs("documents", exist_ok=True)
    file_path = os.path.join("documents", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Run the ingestion pipeline for the newly uploaded file
        run_ingestion(file_path)
        return {"message": f"Successfully uploaded and ingested {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
