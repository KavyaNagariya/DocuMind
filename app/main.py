from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
import shutil
from app.services.rag_service import RAGService
from app.ingest_docs import run_ingestion
from pydantic import BaseModel

app = FastAPI(title="Documind Enterprise v1.0")
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
async def upload_documents(files: List[UploadFile] = File(...)):
    os.makedirs("documents", exist_ok=True)
    uploaded_files = []
    
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF. Only PDF files are supported.")
        
        file_path = os.path.join("documents", file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Run the ingestion pipeline for the newly uploaded file
            run_ingestion(file_path)
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingestion failed for {file.filename}: {str(e)}")
            
    return {"message": f"Successfully uploaded and ingested {len(uploaded_files)} files.", "files": uploaded_files}
