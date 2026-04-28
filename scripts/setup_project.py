import os
import asyncio
from huggingface_hub import snapshot_download
from app.database import engine, Base
from app.ingestion import load_document, chunk_documents, create_vector_store
# Import models to ensure they are registered with Base.metadata
from app.models import Feedback

async def initialize_database():
    """
    Initialize the SQLite database by creating all tables.
    """
    print("Initializing SQLite database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialization complete.")

def check_and_download_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2", local_dir: str = "models/all-MiniLM-L6-v2"):
    """
    Check if the embedding model exists locally; if not, download it.
    """
    if os.path.exists(local_dir) and len(os.listdir(local_dir)) > 0:
        print(f"Model found at {local_dir}. Skipping download.")
    else:
        print(f"Model not found at {local_dir}. Downloading {model_name}...")
        snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print("Download complete.")

def run_ingestion(data_dir: str, persist_db: str):
    """
    Load all supported documents from data_dir and save them to chroma_db.
    """
    all_documents = []
    supported_exts = [".pdf", ".md", ".docx", ".txt"]
    
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} does not exist. Skipping ingestion.")
        return

    print(f"Scanning directory: {data_dir}")
    for file in os.listdir(data_dir):
        ext = os.path.splitext(file)[1].lower()
        if ext in supported_exts:
            file_path = os.path.join(data_dir, file)
            print(f"Loading: {file_path}")
            try:
                docs = load_document(file_path)
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    if not all_documents:
        print("No supported documents found in the data directory.")
        return

    print(f"Total documents loaded: {len(all_documents)}")
    print("Chunking documents...")
    chunks = chunk_documents(all_documents)
    print(f"Created {len(chunks)} chunks.")

    print(f"Creating and persisting vector store at {persist_db}...")
    create_vector_store(chunks, persist_directory=persist_db)
    print("Ingestion complete.")

async def run_setup(data_dir: str = "data", persist_db: str = "chroma_db"):
    """
    Run the full project setup: Model check, DB initialization and ingestion.
    """
    print("=== LangGraph RAG Project Setup ===")
    check_and_download_model()
    await initialize_database()
    run_ingestion(data_dir, persist_db)
    print("=== Setup Finished Successfully ===")

if __name__ == "__main__":
    asyncio.run(run_setup())
