from fastapi import FastAPI
from app.services.rag_service import RAGService
from pydantic import BaseModel


app = FastAPI()
rag_service = RAGService()


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.post("/chat")
async def chat(request: ChatRequest):
    response = rag_service.answer_question(request.message, request.history)
    return {
            "answer": response["answer"],
            "sources": [doc.metadata for doc in response["source_documents"]]
            }
