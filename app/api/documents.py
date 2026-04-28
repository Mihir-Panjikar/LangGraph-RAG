from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_community.vectorstores import Chroma
from app.ingestion import get_embeddings, run_ingestion
import os
import shutil

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
    results = chroma_client.get()
    metadatas = results.get("metadatas", [])
    
    docs_summary = {}
    for meta in metadatas:
        filename = meta.get("filename")
        if not filename:
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

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

from typing import List

@router.post("/ingest")
async def ingest_documents(files: List[UploadFile] = File(None)):
    """
    Ingest new documents or trigger a directory re-scan.
    """
    if files:
        ingested_files = []
        for file in files:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in [".pdf", ".md", ".docx", ".txt"]:
                # We skip invalid files but process the valid ones
                continue
                
            # Ensure data directory exists
            os.makedirs("data", exist_ok=True)
            file_path = os.path.join("data", file.filename)
            save_upload_file(file, file_path)
            
            # Trigger ingestion for the specific file
            run_ingestion(target_path=file_path)
            ingested_files.append(file.filename)
        
        if not ingested_files:
            raise HTTPException(status_code=400, detail="No valid files provided for ingestion.")
            
        return {"message": f"Successfully ingested: {', '.join(ingested_files)}"}
    else:
        # Trigger directory re-scan
        run_ingestion()
        return {"message": "Directory re-scan triggered"}
