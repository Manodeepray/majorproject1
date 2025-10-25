import os
import numpy as np
import hnswlib
import json
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def build_hnsw_index(vector_log, persist_dir="data/vectorstores"):
    """Build and persist an HNSW index from stored vectors."""
    
    vectors = []
    ids = []

    for vector_id, info in vector_log.items():
        vec = np.load(info["embedding_path"])
        vectors.append(vec)
        ids.append(vector_id)

    vectors = np.array(vectors).astype("float32")
    num_elements, dim = vectors.shape

    # Build HNSW index
    index = hnswlib.Index(space='l2', dim=dim)
    index.init_index(max_elements=num_elements, ef_construction=200, M=16)
    index.add_items(vectors, np.arange(num_elements))

    # Persist index
    index_path = os.path.join(persist_dir, "hnsw_index.bin")
    index.save_index(index_path)

    # Save vector ID mapping
    ids_path = os.path.join(persist_dir, "vector_ids.json")
    with open(ids_path, "w") as f:
        json.dump(ids, f, indent=4)

    print(f"✅ HNSW index saved to {index_path}")
    print(f"✅ Vector IDs saved to {ids_path}")

    return index, ids

def load_hnsw_index(persist_dir="data/vectorstores", max_elements=10000, dim=384):
    """Load a persisted HNSW index and vector ID mapping."""
    index_path = os.path.join(persist_dir, "hnsw_index.bin")
    ids_path = os.path.join(persist_dir, "vector_ids.json")

    if not os.path.exists(index_path) or not os.path.exists(ids_path):
        raise FileNotFoundError("HNSW index or vector_ids.json not found. Build the index first.")

    # Load HNSW index
    index = hnswlib.Index(space='l2', dim=dim)
    index.load_index(index_path, max_elements=max_elements)

    # Load vector IDs
    with open(ids_path, "r") as f:
        ids = json.load(f)

    print(f"✅ HNSW index and vector IDs loaded from {persist_dir}")
    return index, ids

def search_hnsw_index(query, index, ids, vector_log, top_k=5):
    """Retrieve top-k most similar chunks to a query using HNSW."""
    query_vector = embedding_model.encode(query).astype('float32').reshape(1, -1)
    labels, distances = index.knn_query(query_vector, k=top_k)
    
    results = []
    for label, dist in zip(labels[0], distances[0]):
        vector_id = ids[label]
        results.append({
            "vector_id": vector_id,
            "file_name": vector_log[vector_id]["file_name"],
            "chunk_id": vector_log[vector_id]["chunk_id"],
            "metadata": vector_log[vector_id]["metadata"],
            "distance": float(dist)
        })
    return results
