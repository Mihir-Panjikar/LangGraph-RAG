from fastapi import APIRouter
from langchain_community.vectorstores import Chroma
from app.ingestion import get_embeddings
import os

router = APIRouter()

# Global Chroma client for the router
persist_directory = "chroma_db"
embeddings = get_embeddings()

# We export this so it can be mocked in tests
chroma_client = Chroma(
    persist_directory=persist_directory, 
    embedding_function=embeddings
)._collection

@router.get("/documents")
async def list_documents():
    """
    List all indexed documents with their metadata.
    """
    # Use get() on the collection to retrieve all documents
    # Note: Depending on collection size, you might want to limit this
    results = chroma_client.get()
    
    metadatas = results.get("metadatas", [])
    
    # Process metadata to group by unique filenames
    docs_summary = {}
    for meta in metadatas:
        filename = meta.get("filename")
        if not filename:
            # Fallback to source if filename is missing
            source = meta.get("source", "Unknown")
            filename = os.path.basename(source)
        
        if filename not in docs_summary:
            docs_summary[filename] = {
                "filename": filename,
                "chunk_count": 0,
                "timestamp": meta.get("timestamp", "Unknown")
            }
        docs_summary[filename]["chunk_count"] += 1
        
    return list(docs_summary.values())
