from pinecone import Pinecone, ServerlessSpec
import os


def init_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "documind-enterprise")

    if index_name not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )
    return pc.Index(index_name)
