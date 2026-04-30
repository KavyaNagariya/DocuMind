from pinecone import Pinecone, ServerlessSpec
import os


def init_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "documing-enterprise"

    if index_name not in pc.list_indexes().names():
        pc.create_index(
                name=index_name,
                dimensions=384,
                metric="cosine",
                specs=ServerlessSpec(cloud="aws", region="us-east-1")
                )
    return pc.Index(index_name)
