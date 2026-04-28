# LangGraph RAG Documentation Assistant

A high-performance, self-corrective Retrieval-Augmented Generation (RAG) system designed to answer technical documentation queries with precision. Built with **LangGraph**, **FastAPI**, and **ChromaDB**, this project implements an "Agentic RAG" workflow that can self-evaluate and refine its answers.

## Key Features

- **Agentic Orchestration:** Uses LangGraph to manage a cyclic state machine for complex RAG workflows, including retrieval grading and query transformation.
- **Multi-Format Ingestion:** Seamlessly processes PDF, Markdown, Microsoft Word (.docx), and Plain Text files.
- **Semantic Chunking:** Implements a structural, two-pass splitting strategy to preserve document context and hierarchy.
- **Offline-First Embeddings:** Utilizes local Hugging Face `all-MiniLM-L6-v2` models for privacy and consistent performance without external API latency.
- **Self-Correction:** Automatically grades retrieved documents and hallucination checks on generated answers to ensure high fidelity.
- **Modern Backend:** Served via a robust FastAPI layer with auto-generated OpenAPI documentation.

---

## Setup & Installation

### 1. Prerequisites
Ensure you have `uv` installed. If not, install it via:
```powershell
powershell -c "ir | iex" # Windows
# OR
curl -LsSf https://astral.sh/uv/install.sh | sh # Linux/macOS
```

### 2. Environment Setup
Clone the repository and sync dependencies:
```bash
uv sync
```

### 3. API Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Add your `GROQ_API_KEY` to the `.env` file.

### 4. Project Initialization
Run the unified setup script to download models, initialize the database, and ingest the document corpus:
```bash
$env:PYTHONPATH="."; uv run python scripts/setup_project.py
```

---

## Running the Application

Start the FastAPI server:
```bash
uv run python main.py
```
Access the interactive documentation at `http://localhost:8000/docs`.

---

## API Usage Examples

### 1. Query the Assistant
**Endpoint:** `POST /query`
```bash
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "How do I set up the ingestion pipeline?"}'
```
**Response (Streaming):**
Returns a stream of events representing the LangGraph node execution and finally the generated response with citations.

### 2. Ingest New Documents
**Endpoint:** `POST /ingest`
```bash
curl -X POST http://localhost:8000/ingest \
     -F "files=@/path/to/your/doc.pdf"
```

### 3. Submit Feedback
**Endpoint:** `POST /feedback`
```bash
curl -X POST http://localhost:8000/feedback \
     -H "Content-Type: application/json" \
     -d '{"query_id": "uuid-123", "rating": 1, "comment": "Great answer!"}'
```

### 4. List Indexed Documents
**Endpoint:** `GET /documents`
```bash
curl -X GET http://localhost:8000/documents
```
**Response:**
```json
[
  {
    "filename": "programming.txt",
    "chunk_count": 12,
    "timestamp": "2026-04-28T10:00:00"
  }
]
```

---

## Architecture & Design Decisions

### The LangGraph Workflow
The system uses a state machine to orchestrate the RAG lifecycle:
1. **Analyze Query:** Determines if the query is a greeting or a technical question.
2. **Retrieve:** Fetches relevant chunks from ChromaDB using semantic similarity.
3. **Grade Documents:** An LLM-powered grader filters out irrelevant chunks.
4. **Transform Query:** If no relevant documents are found, the LLM rewrites the query to improve retrieval.
5. **Generate:** Produces a final answer grounded strictly in the retrieved context, including citations.

### Key Design Choices
- **Two-Pass Chunking:** Combines Markdown header splitting with recursive character splitting to maintain structural context.
- **Local Embeddings:** Chose `all-MiniLM-L6-v2` for its speed and local execution, ensuring data privacy.
- **Self-Correction Loop:** Implemented a retry limit (3) on query transformation to prevent infinite loops while allowing the system to "try again" with better queries.
- **SQLite for Feedback:** Selected a lightweight, persistent storage for user feedback to enable future system evaluation without complex infrastructure.

---

## Future Improvements
- **Web Search Integration:** Add a "Web Search" node as a fallback when local documentation is insufficient.

