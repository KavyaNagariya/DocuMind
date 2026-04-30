import os
from dotenv import load_dotenv
from app.ingestion.loader import load_pdf
from app.ingestion.splitter import get_text_chunks 
from app.ingestion.embedder import get_embedding_model
from langchain_pinecone import PineconeVectorStore

load_dotenv()

def run_ingestion(document_path: str):
    # 1. Validation Check
    if not os.path.exists(document_path):
        print(f"❌ Error: File not found at {document_path}")
        return

    print(f"🚀 Starting Ingestion for: {document_path}")

    # 2. Extract[cite: 1]
    raw_docs = load_pdf(document_path)
    print(f"✅ Loaded {len(raw_docs)} pages.")

    # 3. Transform[cite: 1]
    chunks = get_text_chunks(raw_docs)
    print(f"✅ Created {len(chunks)} text chunks.")

    # 4. Initialize Embedder[cite: 1]
    embeddings = get_embedding_model()
    
    # 5. Load (Upsert) to Pinecone[cite: 1]
    # We use .from_documents because it handles UUIDs and Metadata mapping for us.
    index_name = "documind-enterprise"
    
    print("📡 Uploading to Pinecone... This might take some moments.")
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace="default" 
    )
    
    print("-" * 50)
    print("🎉 Ingestion complete! Your SOP is now searchable.")
    print("-" * 50)

if __name__ == "__main__":
    # Ensure running this from the root folder
    run_ingestion("documents/Test.pdf")
