from fastapi import FastAPI
from app.services.rag_service import RAGService
from pydantic import BaseModel


app = FastAPI(title="Documind Enterprise v1.0")
rag_service = RAGService()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
async def chat(request: ChatRequest):
    result = rag_service.answer_question(request.message, request.history)
    return {
            "answer": result["answer"],
            "citations": [
                {"sources": doc.metadata.get("source"), "page": doc.metadata.get("page")}
                for doc in result["context"]
            ]
    }
