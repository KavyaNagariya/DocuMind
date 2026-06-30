<div align="center">

# DocuMind Enterprise

DocuMind Enterprise is a production-grade, context-aware Retrieval-Augmented Generation (RAG) platform designed to search and interact with private document archives securely.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.1.7-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4.2.1-38bdf8?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.x-1C3C3A?style=flat-square)](https://langchain.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.5--flash-4285F4?style=flat-square&logo=googlegemini)](https://deepmind.google/technologies/gemini/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-black?style=flat-square)](https://www.pinecone.io)

[Overview](#overview) • [Key Features](#key-features) • [Tech Stack](#tech-stack) • [Getting Started](#getting-started) • [Project Structure](#project-structure) • [Usage](#usage)

</div>

---

## Overview

DocuMind Enterprise solves the challenge of employees manually sifting through hundreds of pages of corporate documentation (such as policies, guides, and SOPs). Ingesting this knowledge allows the platform to provide direct, fully-cited answers through an interactive web-based chat.

> [!IMPORTANT]
> **Anti-Hallucination Policy**: To ensure trust and compliance, the system is strictly constrained to the ingested documents. If a question cannot be answered using the provided context, the model will refuse to answer rather than inventing facts.

---

## Key Features

- **Context-Locked RAG**: Utilizes a strict system contract prompting [RAGService](file:///C:/repositories/DocuMind_Enterprise/app/services/rag_service.py) to refuse answers not explicitly supported by context.
- **Contextual Query Rephrasing**: Automatically resolves pronouns and context references (e.g., "it", "then") in conversation history, generating independent keyword-rich search queries.
- **Verified Citations**: Injects page numbers, file sources, and text snippets into response metadata so every claim is instantly auditable.
- **Real-Time Streaming**: Real-time token streaming using Server-Sent Events (SSE) for a premium UI typewriter effect.
- **Built-in Rate Limiting**: Abuse prevention limiting users to 5 requests per minute using `slowapi`.
- **Dockerized Architecture**: Simplified deployment using multi-stage builds and shared volumes for instant local setups.

---

## Tech Stack

- **Backend**: FastAPI web framework, LangChain (v0.3.x), Pydantic
- **Frontend**: Next.js 16 (App Router), React 19, TailwindCSS, Radix UI, Shadcn UI
- **Embeddings & Model**: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`) mapped to CPU, running on Google Gemini (`gemini-2.5-flash`)
- **Database**: Pinecone serverless vector index

---

## Getting Started

### Prerequisites

- Python 3.10+ (if running manually)
- Docker & Docker Compose
- API Keys: Pinecone API Key, Google AI Studio Key (Gemini), HuggingFace Token

### Environment Configuration

Configure your environment variables in [.env](file:///C:/repositories/DocuMind_Enterprise/.env):

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

### Docker Deployment (Recommended)

1. Build and run containers in detached mode:
   ```bash
   docker-compose up --build -d
   ```
2. Access the applications:
   - Frontend Client: [http://localhost:3000](http://localhost:3000)
   - Interactive Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
3. Tear down the stack:
   ```bash
   docker-compose down
   ```

### Manual Local Setup

If you prefer running services independently:

#### 1. Backend Server
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix:
   source venv/bin/activate
   ```
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Boot the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### 2. Frontend Client
1. Install client dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Launch the dev server:
   ```bash
   npm run dev
   ```

---

## Project Structure

- **[app/](file:///C:/repositories/DocuMind_Enterprise/app)**: Core FastAPI application.
  - **[app/main.py](file:///C:/repositories/DocuMind_Enterprise/app/main.py)**: REST API endpoints (`/chat`, `/upload`) with rate limiting.
  - **[app/services/rag_service.py](file:///C:/repositories/DocuMind_Enterprise/app/services/rag_service.py)**: Implements history-aware context rephrasing and streaming QA retrieval chains.
  - **[app/ingest_docs.py](file:///C:/repositories/DocuMind_Enterprise/app/ingest_docs.py)**: Processing script orchestrating document chunking and indexing.
- **[frontend/](file:///C:/repositories/DocuMind_Enterprise/frontend)**: Next.js client application styled with TailwindCSS & Shadcn UI components.
- **[documents/](file:///C:/repositories/DocuMind_Enterprise/documents)**: Local folder holding the source PDF files (volume-mapped in Docker).

---

## Usage

### Document Ingestion

Place target PDF documents in the `documents/` directory, then process them into Pinecone:

- **Via GUI**: Use the document upload option directly inside the web client.
- **Via CLI**:
  ```bash
  python -m app.ingest_docs
  ```

### API Rate Limit Testing

> [!TIP]
> The `/chat` and `/upload` endpoints limit requests to 5 per minute per IP address. You can run the rate-limiting verification script to inspect this behavior:
> ```bash
> python test_rate_limit.py
> ```

