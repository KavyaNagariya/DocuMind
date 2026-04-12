from ingestion.loader import load_pdf
from ingestion.splitter import split_documents

docs = load_pdf("documents/Test.pdf")
chunks = split_documents(docs)


print(f"Total chunks: {len(chunks)}")
print(chunks[0].page_content)
