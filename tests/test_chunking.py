import pytest
from langchain_core.documents import Document
from app.ingestion import chunk_documents

def test_chunk_markdown_documents():
    content = "# Header 1\n\nThis is a paragraph under header 1.\n\n## Header 2\n\nThis is a paragraph under header 2."
    doc = Document(page_content=content, metadata={"source": "test.md"})
    
    chunks = chunk_documents([doc])
    
    # We expect chunks to be separated by headers if using MarkdownHeaderTextSplitter
    assert len(chunks) >= 2
    # Verify metadata contains headers if possible, or at least source
    assert chunks[0].metadata["source"] == "test.md"
    assert any("Header 1" in str(c.metadata) or "Header 1" in c.page_content for c in chunks)

def test_chunk_text_documents():
    content = "A" * 2000 # Long content
    doc = Document(page_content=content, metadata={"source": "test.txt"})
    
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=50)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 550 # roughly chunk_size + some margin
