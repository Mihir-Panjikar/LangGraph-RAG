import pytest
import os
import shutil
from app.ingestion import run_ingestion
from langchain_community.vectorstores import Chroma
from app.ingestion import get_embeddings

def test_run_ingestion_integration(tmp_path):
    # Setup temporary data directory
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()
    sample_file = test_data_dir / "test.md"
    sample_file.write_text("# Test Title\nThis is a test document.")
    
    # Setup temporary chroma directory
    test_chroma_db = tmp_path / "chroma_db"
    
    # Run ingestion
    run_ingestion(
        target_path=str(sample_file),
        data_dir=str(test_data_dir),
        persist_db=str(test_chroma_db)
    )
    
    # Verify vector store
    embeddings = get_embeddings()
    vector_store = Chroma(
        persist_directory=str(test_chroma_db),
        embedding_function=embeddings
    )
    
    results = vector_store.similarity_search("test document", k=1)
    assert len(results) > 0
    assert "Test Title" in results[0].page_content
    assert results[0].metadata["filename"] == "test.md"
