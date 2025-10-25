import os
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer


VECTORSTORE_DIR = "data/vectorstores"
os.makedirs(VECTORSTORE_DIR, exist_ok=True)





def build_faiss_index(vector_log, persist_dir=VECTORSTORE_DIR):
    """Build and persist a FAISS index from stored vectors."""
    




    DATA_WAREHOUSE_DIR = "database/data_warehouse"
    VECTOR_DB_DIR = "database/vectordb"

    DATA_LOGS_DIR = "database/logs"




    VECTOR_LOG_PATH = os.path.join(DATA_LOGS_DIR, "vector_log.json")
    CHUNK_TRACES_PATH = os.path.join(DATA_LOGS_DIR, "chunk_traces.json")
    def ensure_json_file(path):
        if not os.path.exists(path):
            print(f"Creating missing file: {path}")
            with open(path, "w") as f:
                json.dump({}, f, indent=4)  # create an empty JSON object

    # Create the files if they don’t exist
    ensure_json_file(VECTOR_LOG_PATH)
    ensure_json_file(CHUNK_TRACES_PATH)
    # Create directories if not exist
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    # Load model
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Load chunk metadata
    if os.path.exists(CHUNK_TRACES_PATH):
        with open(CHUNK_TRACES_PATH, "r") as f:
            chunk_tracker = json.load(f)
    else:
        raise FileNotFoundError("Chunk tracker not found. Please run the chunking step first.")

    # Load or initialize vector log
    if os.path.exists(VECTOR_LOG_PATH):
        with open(VECTOR_LOG_PATH, "r") as f:
            vector_log = json.load(f)
    else:
        vector_log = {}




    vectors = []
    ids = []

    for vector_id, info in vector_log.items():
        vec = np.load(info["embedding_path"])
        vectors.append(vec)
        ids.append(vector_id)

    vectors = np.array(vectors).astype("float32")

    # Build FAISS index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    # Persist index
    index_path = os.path.join(persist_dir, "faiss_index.idx")
    faiss.write_index(index, index_path)

    # Save vector ID mapping
    ids_path = os.path.join(persist_dir, "vector_ids.json")
    with open(ids_path, "w") as f:
        json.dump(ids, f, indent=4)

    print(f"✅ FAISS index saved to {index_path}")
    print(f"✅ Vector IDs saved to {ids_path}")

    return index, ids
    
    
def search_similar_chunks(query, index, ids, vector_log, top_k=5):
    """Retrieve top-k most similar chunks to a query."""
    query_vector = embedding_model.encode(query).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        vector_id = ids[idx]
        results.append({
            "vector_id": vector_id,
            "file_name": vector_log[vector_id]["file_name"],
            "chunk_id": vector_log[vector_id]["chunk_id"],
            "metadata": vector_log[vector_id]["metadata"],
            "distance": float(dist)
        })
    return results

# Build index once
def load_vectorstore(persist_dir=VECTORSTORE_DIR):
    """Load a persisted FAISS index and vector ID mapping."""
    index_path = os.path.join(persist_dir, "faiss_index.idx")
    ids_path = os.path.join(persist_dir, "vector_ids.json")

    if not os.path.exists(index_path) or not os.path.exists(ids_path):
        raise FileNotFoundError("FAISS index or vector_ids.json not found. Build the index first.")

    # Load FAISS index
    index = faiss.read_index(index_path)

    # Load vector IDs
    with open(ids_path, "r") as f:
        ids = json.load(f)

    print(f"✅ FAISS index and vector IDs loaded from {persist_dir}")
    return index, ids

if __name__ == "__main__":
    index, ids = build_faiss_index(vector_log)

    # Example usage:
    index, ids = load_vectorstore(VECTORSTORE_DIR)

    # Example search function (needs compute_embedding and vector_log defined)
    query = "indian histiry process"
    results = search_similar_chunks(query, index, ids, vector_log)
    print(json.dumps(results, indent=4))
