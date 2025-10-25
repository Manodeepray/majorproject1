import os
from huggingface_hub import hf_hub_download

MODEL_LIST = [
    {
        "repo_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "filename": "qwen2.5-0.5b-instruct-q4_k_m.gguf",
        "local_dir": os.path.join(os.path.expanduser("~"), ".cache", "qwen")
    }
]

def check():
    for model in MODEL_LIST:
        try:
            print(f"[models] Downloading {model['repo_id']}/{model['filename']} ...")
            local_path = hf_hub_download(
                repo_id=model["repo_id"],
                filename=model["filename"],
                cache_dir=model["local_dir"]
            )
            print(f"[models] Saved to {local_path}")
        except Exception as e:
            print(f"[ERROR] Failed to download {model['repo_id']}: {e}")
            
            
if __name__ == "__main__":
    check()
    
    
    
