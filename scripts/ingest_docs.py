import os
from app.ingestion import load_document, chunk_documents, create_vector_store

def run_ingestion(data_dir: str, persist_db: str):
    """
    Load all supported documents from data_dir and save them to chroma_db.
    """
    all_documents = []
    supported_exts = [".pdf", ".md", ".docx", ".txt"]
    
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
    
    print(f"Total documents loaded: {len(all_documents)}")
    print("Chunking documents...")
    chunks = chunk_documents(all_documents)
    print(f"Created {len(chunks)} chunks.")
    
    print(f"Creating and persisting vector store at {persist_db}...")
    create_vector_store(chunks, persist_directory=persist_db)
    print("Ingestion complete.")

if __name__ == "__main__":
    run_ingestion("data", "chroma_db")
