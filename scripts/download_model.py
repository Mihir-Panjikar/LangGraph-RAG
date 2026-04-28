from huggingface_hub import snapshot_download
import os

def download_model(model_name: str, local_dir: str):
    print(f"Downloading {model_name} to {local_dir}...")
    snapshot_download(
        repo_id=model_name,
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
    print("Download complete.")

if __name__ == "__main__":
    download_model("sentence-transformers/all-MiniLM-L6-v2", "models/all-MiniLM-L6-v2")
