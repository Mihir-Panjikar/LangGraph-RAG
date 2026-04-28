"""
Synchronous API client for the FastAPI backend.

Uses httpx sync client because Streamlit runs its own event loop;
calling asyncio.run() inside Streamlit causes RuntimeError.
"""
import httpx
from typing import Iterator, Any

API_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 60.0


def query_backend_stream(query: str) -> Iterator[str]:
    """Stream tokens from the /query endpoint."""
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        with client.stream(
            "POST", f"{API_BASE_URL}/query", json={"query": query}
        ) as response:
            response.raise_for_status()
            for chunk in response.iter_text():
                if chunk:
                    yield chunk


def ingest_document(file_name: str, file_content: bytes) -> dict[str, Any]:
    """Upload a document to the /ingest endpoint."""
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        files = [("files", (file_name, file_content))]
        response = client.post(f"{API_BASE_URL}/ingest", files=files)
        response.raise_for_status()
        return response.json()


def get_documents() -> list[dict[str, Any]]:
    """Fetch the list of ingested documents from /documents."""
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.get(f"{API_BASE_URL}/documents")
        response.raise_for_status()
        return response.json()


def submit_feedback(query_id: str, rating: int, comment: str | None = None) -> dict[str, Any]:
    """Submit feedback for a specific query to /feedback."""
    payload = {"query_id": query_id, "rating": rating}
    if comment:
        payload["comment"] = comment
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.post(f"{API_BASE_URL}/feedback", json=payload)
        response.raise_for_status()
        return response.json()


def check_backend_health() -> bool:
    """Quick connectivity check against the backend root."""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{API_BASE_URL}/")
            return response.status_code == 200
    except httpx.HTTPError:
        return False