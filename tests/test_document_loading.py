import pytest
import os
from app.ingestion import load_document

def test_load_text_document(tmp_path):
    d = tmp_path / "test.txt"
    content = "Hello world"
    d.write_text(content)
    
    docs = load_document(str(d))
    assert len(docs) == 1
    assert docs[0].page_content == content
    assert docs[0].metadata["source"] == str(d)

def test_load_markdown_document(tmp_path):
    d = tmp_path / "test.md"
    content = "# Header\n\nContent"
    d.write_text(content)
    
    docs = load_document(str(d))
    assert len(docs) == 1
    assert "Header" in docs[0].page_content
    assert docs[0].metadata["source"] == str(d)

def test_load_docx_document():
    # We will use the sample in data/
    path = "data/Graphic User Interface FAQ.docx"
    if os.path.exists(path):
        docs = load_document(path)
        assert len(docs) > 0
        assert docs[0].metadata["source"] == path
    else:
        pytest.skip("Sample docx not found")

def test_load_pdf_document():
    # We will use the sample in data/
    path = "data/General Python FAQ.pdf"
    if os.path.exists(path):
        docs = load_document(path)
        assert len(docs) > 0
        assert docs[0].metadata["source"] == path
    else:
        pytest.skip("Sample pdf not found")

def test_load_unsupported_format(tmp_path):
    d = tmp_path / "test.unknown"
    d.write_text("content")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_document(str(d))
