import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Internal Imports
from app.ingestion.embedder import get_embedding_model
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

app = FastAPI(title="DocuMind Enterprise API")

# --- 1. Infrastructure Initialization ---
# We initialize these ONCE when the server starts, not inside the request.
embeddings = get_embedding_model()
vectorstore = PineconeVectorStore(
    index_name="documind-enterprise", 
    embedding=embeddings
)

# Initialize Gemini 1.5 Flash (Free Tier)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0 # Principal's Tip: Keep temp at 0 for technical SOPs to prevent "creativity"
)

# --- 2. The "Hallucination Guardrail" Prompt ---
# This is the most important part of your project requirements.
template = """
You are the DocuMind Enterprise Assistant. Use the following pieces of context to answer the question.
If the answer is not contained within the context provided below, say exactly: 
"I'm sorry, but that information is not in the corporate documentation." 
Do NOT try to make up an answer or use external knowledge.

CONTEXT:
{context}

QUESTION: 
{question}

HELPFUL ANSWER:
"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

# --- 3. Pydantic Models ---
# Professional APIs use schemas to validate data before it touches the "brain."
class QueryRequest(BaseModel):
    prompt: str

class QueryResponse(BaseModel):
    answer: str
    sources: list

# --- 4. The API Endpoint ---
@app.post("/chat", response_model=QueryResponse)
async def chat_with_docs(request: QueryRequest):
    try:
        # Create the Retrieval Chain
        # This automatically: 1. Embeds question, 2. Searches Pinecone, 3. Prompts Gemini
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
            return_source_documents=True
        )

        result = qa_chain.invoke({"query": request.prompt})
        
        # Extract metadata for citations (Requirement #2)
        sources = [
            {"page": doc.metadata.get("page"), "source": doc.metadata.get("source")}
            for doc in result["source_documents"]
        ]

        return QueryResponse(
            answer=result["result"],
            sources=sources
        )

    except Exception as e:
        # Principal's Tip: Never return raw error strings to the user in production.
        # Log it internally instead.
        print(f"Logging Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error occurred.")
