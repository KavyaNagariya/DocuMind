from ingestion.loader import load_pdf
from ingestion.splitter import split_documents
from ingestion.embedder import get_embedding_model
from ingestion.upsert import get_pinecone_index
import uuid


docs = load_pdf("documents/Test.pdf")
chunks = split_documents(docs)


embedding_model = get_embedding_model()
index = get_pinecone_index()

vectors = []

for chunk in chunks:
    vector = embedding_model.embed_query(chunk.page_content)
    
    vectors.append({
        "id": str(uuid.uuid4()),
        "values": vector,
        "metadata": {
            "text": chunk.page_content,
            "page_number": chunk.metadata.get("page", 0),
            "source": "employee_policy.pdf"
        }
    })
index.upsert(vectors=vectors)


print(f"Uploaded {len(vectors)} chunks to Pinecone")
