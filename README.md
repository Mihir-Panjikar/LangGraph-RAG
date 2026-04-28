# LangGraph RAG Documentation Assistant

A high-performance, self-corrective Retrieval-Augmented Generation (RAG) system designed to answer technical documentation queries with precision. Built with **LangGraph**, **FastAPI**, and **ChromaDB**, this project implements an "Agentic RAG" workflow that can self-evaluate and refine its answers.

## Key Features

- **Agentic Orchestration:** Uses LangGraph to manage a cyclic state machine for complex RAG workflows, including retrieval grading and query transformation.
- **Multi-Format Ingestion:** Seamlessly processes PDF, Markdown, Microsoft Word (.docx), and Plain Text files.
- **Semantic Chunking:** Implements a structural, two-pass splitting strategy to preserve document context and hierarchy.
- **Offline-First Embeddings:** Utilizes local Hugging Face `all-MiniLM-L6-v2` models for privacy and consistent performance without external API latency.
- **Self-Correction:** Automatically grades retrieved documents and hallucinates checks on generated answers to ensure high fidelity.
- **Modern Backend:** Served via a robust FastAPI layer with auto-generated OpenAPI documentation.

## Technical Architecture

- **Orchestration:** LangGraph (StateGraph)
- **Vector Store:** ChromaDB (Local Persistence)
- **Embeddings:** Hugging Face (Sentence Transformers)
- **API Layer:** FastAPI / Uvicorn
- **Package Management:** `uv`

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

### 3. Model Preparation
Download the embedding model to the local `models/` directory:
```bash
uv run scripts/download_model.py
```

### 4. Data Ingestion
Place your technical documentation in the `data/` folder and build the vector index:
```bash
uv run scripts/ingest_docs.py
```

## Running the Application

Start the FastAPI server:
```bash
uv run python main.py
```
Access the interactive documentation at `http://localhost:8000/docs`.

---
*For detailed development milestones, see [project_report.md](./project_report.md).*
