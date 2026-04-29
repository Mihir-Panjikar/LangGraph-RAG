from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    TextLoader
)
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import functools
from datetime import datetime, timezone, timedelta
from typing import List, Optional

def load_document(file_path: str):
    """
    Load a document from the given file path based on its extension.
    Supported formats: .pdf, .md, .docx, .txt
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".md":
        # UnstructuredMarkdownLoader is better for technical content
        loader = UnstructuredMarkdownLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    docs = loader.load()
    # Add timestamp and filename to metadata
    ist = timezone(timedelta(hours=5, minutes=30))
    timestamp = datetime.now(ist).isoformat()
    filename = os.path.basename(file_path)
    for doc in docs:
        doc.metadata["timestamp"] = timestamp
        doc.metadata["filename"] = filename
    return docs

def chunk_documents(documents, chunk_size=1000, chunk_overlap=100):
    """
    Chunk documents using a two-pass strategy:
    1. MarkdownHeaderTextSplitter for semantic sectioning (if applicable)
    2. RecursiveCharacterTextSplitter for size limits
    """
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    final_chunks = []
    
    for doc in documents:
        # If it's markdown or has markdown structure, try semantic splitting
        # For simplicity, we check the source extension if available in metadata
        source = doc.metadata.get("source", "")
        if source.endswith(".md"):
            # MarkdownHeaderTextSplitter returns a list of Documents
            header_splits = markdown_splitter.split_text(doc.page_content)
            # Add back source metadata to header_splits
            for split in header_splits:
                split.metadata.update(doc.metadata)
            # Further split by character limit
            final_chunks.extend(text_splitter.split_documents(header_splits))
        else:
            final_chunks.extend(text_splitter.split_documents([doc]))
            
    return final_chunks

@functools.lru_cache(maxsize=1)
def get_embeddings():
    """
    Initialize HuggingFace embeddings from a local model path.
    Caches the instance to avoid reloading the model.
    """
    model_path = os.path.join("models", "all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_path)

@functools.lru_cache(maxsize=1)
def get_vector_store(persist_directory="chroma_db"):
    """
    Get the Chroma vector store instance. Caches the instance.
    """
    embeddings = get_embeddings()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def create_vector_store(documents, persist_directory="chroma_db"):
    """
    Add documents to the vector store.
    """
    vector_store = get_vector_store(persist_directory)
    vector_store.add_documents(documents=documents)
    return vector_store

def search_vector_store(query, persist_directory="chroma_db", k=3):
    """
    Search the vector store for the most relevant documents.
    """
    vector_store = get_vector_store(persist_directory)
    return vector_store.similarity_search(query, k=k)

def run_ingestion(target_paths: List[str] = None, data_dir: str = "data", persist_db: str = "chroma_db"):
    """
    Ingest documents from target_paths (if provided) or all documents from data_dir.
    """
    all_documents = []
    supported_exts = [".pdf", ".md", ".docx", ".txt"]
    
    if target_paths:
        # Ingest specific files
        for path in target_paths:
            if os.path.isfile(path):
                try:
                    all_documents.extend(load_document(path))
                except Exception:
                    continue
    else:
        # Re-scan directory
        for file in os.listdir(data_dir):
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_exts:
                file_path = os.path.join(data_dir, file)
                try:
                    all_documents.extend(load_document(file_path))
                except Exception:
                    continue
    
    if not all_documents:
        return
        
    chunks = chunk_documents(all_documents)
    create_vector_store(chunks, persist_directory=persist_db)
