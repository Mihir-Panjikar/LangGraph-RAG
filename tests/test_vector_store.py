import pytest
from langchain_core.documents import Document
from app.ingestion import create_vector_store, search_vector_store
import os
import shutil

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_chroma_db")

def test_create_and_search_vector_store(db_path):
    docs = [
        Document(page_content="Python is a programming language.", metadata={"source": "a.txt"}),
        Document(page_content="London is the capital of England.", metadata={"source": "b.txt"}),
    ]
    
    vector_store = create_vector_store(docs, persist_directory=db_path)
    
    # Search for something relevant to the first doc
    results = search_vector_store("What is Python?", persist_directory=db_path)
    
    assert len(results) > 0
    assert "programming language" in results[0].page_content
    assert results[0].metadata["source"] == "a.txt"
