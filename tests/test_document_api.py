import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from main import app

client = TestClient(app)

@pytest.fixture
def mock_chroma():
    with patch("app.api.documents.chroma_client") as mock:
        yield mock

def test_get_documents_empty(mock_chroma):
    # Mock ChromaDB to return no documents
    mock_chroma.get.return_value = {"ids": [], "metadatas": []}
    
    response = client.get("/documents")
    assert response.status_code == 200
    assert response.json() == []

def test_get_documents_with_data(mock_chroma):
    # Mock ChromaDB to return some documents
    mock_chroma.get.return_value = {
        "ids": ["doc1", "doc2"],
        "metadatas": [
            {"filename": "test1.pdf", "timestamp": "2026-04-28T12:00:00"},
            {"filename": "test2.md", "timestamp": "2026-04-28T13:00:00"}
        ]
    }
    
    response = client.get("/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["filename"] == "test1.pdf"
    assert data[1]["filename"] == "test2.md"
