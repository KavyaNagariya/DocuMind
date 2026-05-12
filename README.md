# DocuMind Enterprise

DocuMind Enterprise is a robust, production-grade Retrieval-Augmented Generation (RAG) application designed to search and interact with your private document archives. Built with FastAPI, LangChain, and Pinecone, it provides a powerful chat interface that handles complex multi-turn conversations with source citations.

## 🚀 Features

- **Advanced RAG Pipeline:** Uses LangChain (v0.3.x) for efficient document retrieval and response generation.
- **Contextual Query Rephrasing:** Automatically resolves references (like "it", "him", "then") in chat history to generate standalone search queries.
- **Source Citations:** Every answer includes references to the specific documents and pages used to generate the response.
- **API Rate Limiting:** Built-in protection against abuse using `slowapi` (5 requests/minute).
- **Chat Management:** Create, rename, and delete chat sessions with persistent local storage.
- **Pinecone Vector Store:** High-performance serverless vector search for lightning-fast retrievals.
- **FastAPI Backend:** Modern, high-performance web API for seamless integration.
- **Document Ingestion:** Automated pipeline for loading, splitting, and indexing PDF documents.

## 🛠️ Tech Stack

- **Framework:** FastAPI
- **RAG Engine:** LangChain (v0.3.x)
- **LLM:** Google Gemini (via `gemini-2.5-flash`)
- **Vector Database:** Pinecone
- **Embeddings:** HuggingFace (`all-MiniLM-L6-v2`)
- **Frontend:** Next.js 15 (App Router), TailwindCSS, Shadcn UI
- **Document Processing:** pypdf

## 📋 Prerequisites

- Python 3.10+ (for local setup)
- Docker & Docker Compose (for containerized setup)
- [Pinecone API Key](https://www.pinecone.io/)
- [Google AI API Key](https://aistudio.google.com/) (for Gemini)
- [HuggingFace Token](https://huggingface.co/settings/tokens) (for model access)

## 🔧 Configuration

Create a `.env` file in the root directory and add the following:

```env
# AI & Database Keys
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
HF_TOKEN=your_huggingface_token

# Application Config
PINECONE_INDEX_NAME=documind-enterprise
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐳 Docker Deployment (Recommended)

The easiest way to run the entire stack is using Docker Compose.

1. **Build and start the containers:**
   ```bash
   docker-compose up --build -d
   ```

2. **Access the application:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

3. **Stop the containers:**
   ```bash
   docker-compose down
   ```

---

## ⚙️ Local Installation

If you prefer to run the services manually:

### 1. Backend Setup
1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Frontend Setup
1. **Install dependencies:**
   ```bash
   cd frontend
   npm install  # or bun install
   ```
2. **Run the development server:**
   ```bash
   npm run dev  # or bun run dev
   ```

---

## 📖 Usage

### 1. Ingest Documents
Place your PDF files in the `documents/` directory. You can use the UI to upload files or run the ingestion script manually:

```bash
python -m app.ingest_docs
```

### 2. Rate Limiting
The API is restricted to **5 requests per minute** per user. You can test this using the provided script:
```bash
python test_rate_limit.py
```

## 🛣️ API Endpoints

### `POST /chat`
Interact with the RAG service. Supports streaming responses and citations.

### `POST /upload`
Upload multiple PDF documents for automated ingestion.

## 📁 Project Structure

- `app/`: FastAPI backend implementation.
- `frontend/`: Next.js frontend application.
- `documents/`: Directory for source PDF documents (synced with Docker volume).
- `test_rate_limit.py`: Utility script to verify API rate limiting.
