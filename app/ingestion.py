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
        
    return loader.load()

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

def get_embeddings():
    """
    Initialize HuggingFace embeddings from a local model path.
    """
    model_path = os.path.join("models", "all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model_path)

def create_vector_store(documents, persist_directory="chroma_db"):
    """
    Create a vector store from documents and persist it.
    """
    embeddings = get_embeddings()
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    return vector_store

def search_vector_store(query, persist_directory="chroma_db", k=3):
    """
    Search the vector store for the most relevant documents.
    """
    embeddings = get_embeddings()
    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    return vector_store.similarity_search(query, k=k)
