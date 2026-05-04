# DocuMind Enterprise

DocuMind Enterprise is a robust, production-grade Retrieval-Augmented Generation (RAG) application designed to search and interact with your private document archives. Built with FastAPI, LangChain, and Pinecone, it provides a powerful chat interface that handles complex multi-turn conversations with source citations.

## 🚀 Features

- **Advanced RAG Pipeline:** Uses LangChain (v0.3.x) for efficient document retrieval and response generation.
- **Contextual Query Rephrasing:** Automatically resolves references (like "it", "him", "then") in chat history to generate standalone search queries.
- **Source Citations:** Every answer includes references to the specific documents and pages used to generate the response.
- **Pinecone Vector Store:** High-performance serverless vector search for lightning-fast retrievals.
- **FastAPI Backend:** Modern, high-performance web API for seamless integration.
- **Document Ingestion:** Automated pipeline for loading, splitting, and indexing PDF documents.

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **RAG Engine:** LangChain (v0.3.x)
- **LLM:** Google Gemini (via `gemini-2.5-flash`)
- **Vector Database:** Pinecone
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
- **Document Processing:** pypdf

## 📋 Prerequisites

- Python 3.10+
- [Pinecone API Key](https://www.pinecone.io/)
- [Google AI API Key](https://aistudio.google.com/) (for Gemini)

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd DocuMind_Enterprise
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuration

Create a `.env` file in the root directory and add the following:

```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=documind-enterprise
```

## 📖 Usage

### 1. Ingest Documents
Place your PDF files in the `documents/` directory. By default, the system indexes `documents/Test.pdf`.

```bash
python -m app.ingest_docs
```

### 2. Run the Server
Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`.

## 🛣️ API Endpoints

### `POST /chat`
Interact with the RAG service.

**Request Body:**
```json
{
  "message": "What are the key points in the SOP?",
  "history": []
}
```

**Response:**
```json
{
  "answer": "The key points include...",
  "citations": [
    {
      "sources": "documents/Test.pdf",
      "page": 1,
      "snippet": "..."
    }
  ]
}
```

## 📁 Project Structure

- `app/`
  - `main.py`: FastAPI application entry point.
  - `config.py`: Initial Pinecone index setup.
  - `ingest_docs.py`: Document ingestion script.
  - `core/`
    - `config.py`: LLM and Embedding initialization.
    - `prompts.py`: System prompts for RAG.
  - `ingestion/`: Logic for loading, splitting, and embedding.
  - `services/`: Core RAG service implementation.
- `documents/`: Directory for source PDF documents.
- `graphify-out/`: Knowledge graph visualizations (generated).
