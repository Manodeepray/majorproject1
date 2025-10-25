import os
import json
import hashlib
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from pathlib import Path
from src.retriever import hnsw_vector_store, faiss_vector_store


class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# === Load embedding model ===
try:
    print(f"\n{Colors.CYAN}[INFO]{Colors.RESET} Loading SentenceTransformer model...")
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} Model loaded successfully.")
except Exception as e:
    print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to load model: {e}")
    raise


def compute_embedding(text):
    """Compute embeddings for a chunk using SentenceTransformer."""
    return embedding_model.encode(text)


def generate_vector_id(file_name, chunk_id):
    """Create a reproducible vector ID."""
    return hashlib.md5(f"{file_name}_{chunk_id}".encode()).hexdigest()


def save_vector(vector: np.ndarray, vector_id: str, VECTOR_DB_DIR):
    """Save vector as a NumPy file."""
    try:
        path = os.path.join(VECTOR_DB_DIR, f"{vector_id}.npy")
        np.save(path, vector)
        return path
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to save vector {vector_id}: {e}")
        return None


def read_chunk_text(chunk_path: str):
    """Read chunk text content from file."""
    try:
        with open(chunk_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Error reading {chunk_path}: {e}")
        return ""


# === Embedding Pipeline ===
def create_vector_db(LOG_DIR, VECTOR_DB_DIR):
    """Traverse chunk_traces.json and generate embeddings for all chunks."""
    CHUNK_TRACES_PATH = LOG_DIR / "chunk_traces.json"
    VECTOR_LOG_PATH = LOG_DIR / "vector_log.json"

    if not CHUNK_TRACES_PATH.exists():
        raise FileNotFoundError(
            f"{Colors.RED}[ERROR]{Colors.RESET} Chunk tracker not found. Please run the chunking step first."
        )

    print(f"\n{Colors.CYAN}[INFO]{Colors.RESET} Loading chunk traces...")
    with open(CHUNK_TRACES_PATH, "r") as f:
        chunk_tracker = json.load(f)

    if os.path.exists(VECTOR_LOG_PATH):
        with open(VECTOR_LOG_PATH, "r") as f:
            vector_log = json.load(f)
    else:
        vector_log = {}

    total_vectors = 0

    for trace_id, chunk_info in tqdm(chunk_tracker.items(), desc="Generating Embeddings"):
        if not chunk_info.get("vectorized", False):
            file_name = chunk_info["file_name"]
            chunk_id = chunk_info["chunk_id"]
            chunk_path = Path(chunk_info["chunk_path"])

            # Generate vector ID
            vector_id = generate_vector_id(file_name, chunk_id)

            # Skip if already embedded
            if vector_id in vector_log:
                chunk_info["vectorized"] = True
                continue

            # Read chunk text
            text = read_chunk_text(chunk_path)
            if not text.strip():
                print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} Empty text in {chunk_path}, skipping.")
                continue

            # Compute embedding safely
            try:
                vector = compute_embedding(text)
            except Exception as e:
                print(f"{Colors.RED}[ERROR]{Colors.RESET} Embedding failed for {chunk_path}: {e}")
                continue

            # Save vector
            vec_path = save_vector(vector, vector_id, VECTOR_DB_DIR)
            if not vec_path:
                continue

            # Build metadata for vector log
            metadata = {
                "source": chunk_info["source"],
                "page_number": chunk_info["page_number"],
                "timestamp": chunk_info["timestamp"],
                "hash": chunk_info["hash"]
            }

            # Update vector log
            vector_log[vector_id] = {
                "file_name": file_name,
                "chunk_id": chunk_id,
                "chunk_path": str(chunk_path),
                "metadata": metadata,
                "embedding_path": str(vec_path)
            }

            # Mark chunk as vectorized
            chunk_info["vectorized"] = True
            total_vectors += 1

    # Save vector log safely
    try:
        with open(VECTOR_LOG_PATH, "w") as f:
            json.dump(vector_log, f, indent=4)
        print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} Embedding complete. Total vectors stored: {len(vector_log)}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to save vector log: {e}")
        return

    # Save updated chunk traces
    try:
        with open(CHUNK_TRACES_PATH, "w") as f:
            json.dump(chunk_tracker, f, indent=4)
        print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} Chunk trace file updated: {CHUNK_TRACES_PATH}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to update chunk trace: {e}")

    print(f"\n{Colors.CYAN}[INFO]{Colors.RESET} Total chunks tracked: {len(chunk_tracker)}, "
          f"Newly vectorized: {total_vectors}")

    # Build indexes safely
    try:
        print(f"\n{Colors.CYAN}[INFO]{Colors.RESET} Building FAISS index...")
        faiss_vector_store.build_faiss_index(vector_log)
        print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} FAISS index built successfully.")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to build FAISS index: {e}")

    try:
        print(f"\n{Colors.CYAN}[INFO]{Colors.RESET} Building HNSW index...")
        hnsw_vector_store.build_hnsw_index(vector_log)
        print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} HNSW index built successfully.")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Failed to build HNSW index: {e}")
