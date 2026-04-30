from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="YOUR_API_KEY")

# Creating the index with professional specs
pc.create_index(
    name="documind-enterprise",
    dimension=384, # Fixed for all-MiniLM-L6-v2
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
