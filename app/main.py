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
