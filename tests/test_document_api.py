import pytest
import os
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

def test_ingest_file_success():
    with patch("app.api.documents.save_upload_file") as mock_save:
        with patch("app.api.documents.run_ingestion") as mock_ingest:
            expected_path = os.path.join("data", "test.pdf")
            mock_save.return_value = expected_path
            
            files = [("files", ("test.pdf", b"pdf content", "application/pdf"))]
            response = client.post("/ingest", files=files)
            
            assert response.status_code == 200
            assert "Successfully ingested: test.pdf" in response.json()["message"]
            mock_ingest.assert_called_once_with(target_path=expected_path)

def test_ingest_invalid_extension():
    files = [("files", ("test.exe", b"binary content", "application/octet-stream"))]
    response = client.post("/ingest", files=files)
    
    assert response.status_code == 400
    assert "No valid files provided" in response.json()["detail"]

def test_ingest_multiple_files_mixed():
    with patch("app.api.documents.save_upload_file") as mock_save:
        with patch("app.api.documents.run_ingestion") as mock_ingest:
            mock_save.side_effect = lambda f, d: d
            
            files = [
                ("files", ("test1.pdf", b"pdf content", "application/pdf")),
                ("files", ("test.exe", b"binary content", "application/octet-stream")),
                ("files", ("test2.txt", b"text content", "text/plain"))
            ]
            response = client.post("/ingest", files=files)
            
            assert response.status_code == 200
            assert "Successfully ingested: test1.pdf, test2.txt" in response.json()["message"]
            assert mock_ingest.call_count == 2

def test_ingest_rescan():
    with patch("app.api.documents.run_ingestion") as mock_ingest:
        response = client.post("/ingest")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Directory re-scan triggered"
        mock_ingest.assert_called_once_with()

def test_save_upload_file(tmp_path):
    from app.api.documents import save_upload_file
    from fastapi import UploadFile
    import io
    
    content = b"test content"
    f = io.BytesIO(content)
    upload_file = UploadFile(filename="test.txt", file=f)
    dest = tmp_path / "test.txt"
    
    path = save_upload_file(upload_file, str(dest))
    
    assert os.path.exists(path)
    with open(path, "rb") as saved:
        assert saved.read() == content
