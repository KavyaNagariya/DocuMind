import os 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.ingestion.embedder import get_embedding_model

load_dotenv()

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Critical: GOOGLE_API_KEY not found in environment. Check your .env file or system variables.")

    return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0,
            safety_settings=None
            )

# Initializing the Embedding model
EMBEDDINGS = get_embedding_model()
