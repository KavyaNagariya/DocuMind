import os 
from lanchain_google_genai import ChatGoogleGenerativeAI
from app.ingestion.embedder import get_embedding_model

def get_llm():
    return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
            )

# Initializing the Embedding model
EMBEDDINGS = get_embedding_model()
