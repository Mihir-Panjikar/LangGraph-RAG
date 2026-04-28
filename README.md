# LangGraph RAG Documentation Assistant

A high-performance, self-corrective Retrieval-Augmented Generation (RAG) system designed to answer technical documentation queries with precision. Built with **LangGraph**, **FastAPI**, **ChromaDB**, and **Streamlit**, this project implements an "Agentic RAG" workflow that can self-evaluate and refine its answers.

## Key Features

- **Agentic Orchestration:** Uses LangGraph to manage a cyclic state machine for complex RAG workflows, including retrieval grading and query transformation.
- **Interactive UI:** A modern Streamlit frontend featuring:
  - **Chat Interface:** Streaming responses with real-time feedback (👍/👎) and source citations.
  - **Document Management:** Upload and ingest new documents (PDF, MD, DOCX, TXT) directly from the UI.
  - **Knowledge Base Viewer:** View and refresh the list of currently indexed documents and chunk counts.
- **Multi-Format Ingestion:** Seamlessly processes PDF, Markdown, Microsoft Word (.docx), and Plain Text files.
- **Semantic Chunking:** Implements a structural, two-pass splitting strategy to preserve document context and hierarchy.
- **Offline-First Embeddings:** Utilizes local Hugging Face `all-MiniLM-L6-v2` models for privacy and consistent performance.
- **Self-Correction:** Automatically grades retrieved documents and performs hallucination checks to ensure high fidelity.
- **Modern Backend:** Robust FastAPI layer with streaming support and auto-generated OpenAPI documentation.

---

## Setup & Installation

### 1. Prerequisites
Ensure you have [uv](https://astral.sh/uv) installed for fast, reliable Python package management.

### 2. Environment Setup
Clone the repository and sync dependencies:
```bash
uv sync
```

### 3. API Configuration
Create a `.env` file from the template:
```bash
cp .env.example .env
```
Add your `GROQ_API_KEY` to the `.env` file. This is used for the LLM reasoning (Llama 3 via Groq).

### 4. Project Initialization
Run the unified setup script to download the embedding model, initialize the SQLite database, and ingest the initial document corpus from the `data/` directory:
```bash
# Windows
$env:PYTHONPATH="."; uv run python scripts/setup_project.py

# Linux/macOS
PYTHONPATH=. uv run python scripts/setup_project.py
```

---

## Running the Application

To use the full system, you need to run both the backend API and the frontend UI.

### 1. Start the FastAPI Backend
```bash
uv run python main.py
```
- **API URL:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`

### 2. Start the Streamlit Frontend
In a new terminal:
```bash
uv run streamlit run frontend/app.py
```
- **Web UI:** `http://localhost:8501`

---

## API Usage Examples

While the UI is the preferred way to interact, you can also use the API directly:

### 1. Query the Assistant
**Endpoint:** `POST /query`
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is RAG?"}'
```

### 2. List Indexed Documents
**Endpoint:** `GET /documents`
```bash
curl -X GET http://localhost:8000/documents
```

---

## Architecture & Design

### The LangGraph Workflow
The system uses a state machine to orchestrate the RAG lifecycle:
1. **Analyze Query:** Determines if the query is a greeting or a technical question.
2. **Retrieve:** Fetches relevant chunks from ChromaDB using semantic similarity.
3. **Grade Documents:** An LLM-powered grader filters out irrelevant chunks.
4. **Transform Query:** If no relevant documents are found, the LLM rewrites the query to improve retrieval.
5. **Generate:** Produces a final answer grounded strictly in the retrieved context, including citations.

### Frontend Integration
The Streamlit frontend uses a synchronous `httpx` client to communicate with the FastAPI backend. This avoids `RuntimeError` conflicts with Streamlit's internal event loop and provides a smooth, streaming chat experience.

### Feedback System
Every chat response includes unique identifiers allowing users to submit helpfulness ratings. This feedback is stored in a local SQLite database for future analysis and system tuning.

---

## Future Improvements
- **Web Search Integration:** Add a "Web Search" node as a fallback when local documentation is insufficient.

