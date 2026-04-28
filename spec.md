# Project Specification: RAG-Based Technical Documentation Assistant

## 1. Project Overview
A self-corrective Retrieval-Augmented Generation (RAG) system built to answer questions based on a selected corpus of technical documentation. The core orchestration is handled by a LangGraph `StateGraph`, served via a FastAPI backend.

## 2. Architecture & LangGraph Workflow

### 2.1 Graph State Definition
The state will be managed using a typed dictionary or Pydantic model containing:
* `original_query` (str): The initial user input.
* `current_query` (str): The actively used query (potentially rewritten).
* `documents` (list): Chunks retrieved from the vector store.
* `relevant_documents` (list): Chunks that passed the grading node.
* `retry_count` (int): Counter to prevent infinite loops (max 3 retries).
* `generation` (str): The final synthesized response.

### 2.2 Core Nodes
1. **Query Analysis:** Rewrites or expands the user query to optimize vector retrieval. Instructed to generate novel search terms if `retry_count > 0`.
2. **Retrieval:** Executes similarity searches against the vector store (ChromaDB) to fetch top-k chunks.
3. **Document Grading (Self-Correction):** Utilizes an LLM structured output to evaluate the relevance of each retrieved chunk. Irrelevant chunks are filtered out.
4. **Generation:** Synthesizes the final answer grounded strictly in the `relevant_documents`. Must include explicit citations referencing chunk metadata.

### 2.3 Routing Logic (Edges)
* **Grading -> Generation:** Triggered if `len(relevant_documents) > 0`.
* **Grading -> Query Analysis (Retry):** Triggered if `len(relevant_documents) == 0` AND `retry_count < MAX_RETRIES`.
* **Grading -> Fallback:** Triggered if `len(relevant_documents) == 0` AND `retry_count >= MAX_RETRIES`. (Returns "I don't know" or triggers optional Web Search).

## 3. Document Ingestion Pipeline
* **Source:** 3-5 technical documents (Markdown/HTML).
* **Chunking Strategy:** Two-pass splitting. `MarkdownHeaderTextSplitter` to preserve semantic sections, followed by `RecursiveCharacterTextSplitter` for size limits.
* **Embeddings & Storage:** Local embedding models stored in a local ChromaDB instance for rapid prototyping.

## 4. API Endpoints (FastAPI)
* `POST /query`: Submits a question, invokes the LangGraph, returns the answer with sources.
* `POST /ingest`: Accepts file uploads or URLs to append to the vector store.
* `GET /documents`: Lists uniquely indexed documents.
* `POST /feedback`: Accepts boolean feedback (thumbs up/down) and optional comments.

## 5. Development Environment
Standard terminal workflows using WSL2 or PowerShell 7 are recommended. To ensure rapid and isolated dependency management, `uv` should be utilized to manage the Python environment and package installations.

## 6. Strict Git Commit Standard
To maintain a clear and evaluable project history, every commit must strictly adhere to the following format. This applies to all commits, whether manually entered or generated via CLI agents.

**Format Pattern:**
`[Type]: [What was added or modified] - [Explanation of why it was added or modified]`

**Format Rules:**
1. **Type:** Must be a standard conventional commit tag (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
2. **What:** Must be a concise, imperative statement of the technical change (e.g., "Implement X", "Change Y").
3. **Why:** Must explicitly state the architectural or functional reason for the change, tying it back to assignment constraints, LangGraph state management, or API requirements.

**Accepted Examples:**
* `feat: Implement document grading node - Required to evaluate chunk relevance and trigger the self-corrective routing fallback.`
* `refactor: Change GraphState to use Pydantic BaseModel - Needed to enforce strict type checking on the retry_count integer during workflow execution.`
* `chore: Add python-multipart dependency - Necessary for the FastAPI /ingest endpoint to accept file uploads.`
