import json
from pathlib import Path
from src.retriever import faiss_vector_store, hnsw_vector_store
from src.retriever.retrieve import retrieve_chunks_from_results

# === Configuration ===
BASE_DIR = Path.cwd()
VECTORSTORE_DIR = BASE_DIR / "data" / "vectorstores"
LOG_DIR = BASE_DIR / "database" / "logs"
VECTOR_LOG_PATH = LOG_DIR / "vector_log.json"
CHUNK_TRACES_PATH = LOG_DIR / "chunk_traces.json"

# === Load Logs ===
def load_logs():
    """Loads vector and chunk trace logs."""
    if not VECTOR_LOG_PATH.exists() or not CHUNK_TRACES_PATH.exists():
        raise FileNotFoundError("Log files not found. Ensure the data ingestion pipeline has been run.")
    
    with open(VECTOR_LOG_PATH, "r") as f:
        vector_log = json.load(f)
    
    with open(CHUNK_TRACES_PATH, "r") as f:
        chunk_traces = json.load(f)
        
    return vector_log, chunk_traces

# === Vector Store Management ===
def load_vector_store(store_type='faiss', persist_dir=VECTORSTORE_DIR):
    """
    Loads the specified vector store (FAISS or HNSW).
    """
    print(f"Attempting to load {store_type.upper()} vector store...")
    if store_type.lower() == 'faiss':
        return faiss_vector_store.load_vectorstore(str(persist_dir))
    elif store_type.lower() == 'hnsw':
        # Note: You might need to pass max_elements and dim if they are not standard
        return hnsw_vector_store.load_hnsw_index(str(persist_dir))
    else:
        raise ValueError("Unsupported store_type. Choose 'faiss' or 'hnsw'.")

# === Retrieval Pipeline ===
def retrieve_chunks(query, index, ids, vector_log, chunk_traces, store_type='faiss', top_k=20):
    """
    Retrieves relevant chunks for a given query.
    """
    print(f"Querying with {store_type.upper()} index...")
    if store_type.lower() == 'faiss':
        similarity_results = faiss_vector_store.search_similar_chunks(query, index, ids, vector_log, top_k)
    elif store_type.lower() == 'hnsw':
        similarity_results = hnsw_vector_store.search_hnsw_index(query, index, ids, vector_log, top_k)
    else:
        raise ValueError("Unsupported store_type. Choose 'faiss' or 'hnsw'.")
        
    retrieved_content = retrieve_chunks_from_results(similarity_results, vector_log, chunk_traces)
    
    return retrieved_content

# === Example Usage ===
if __name__ == '__main__':
    try:
        # 1. Load logs
        vector_log, chunk_traces = load_logs()
        print("✅ Logs loaded successfully.")

        # 2. Load a vector store (e.g., 'faiss' or 'hnsw')
        STORE_CHOICE = 'hnsw' #'faiss'  # or 'hnsw'
        index, ids = load_vector_store(store_type=STORE_CHOICE)
        print(f"✅ {STORE_CHOICE.upper()} vector store loaded.")

        # 3. Formulate a query and retrieve chunks
        query = "What is the main idea of the document?"
        retrieved_data = retrieve_chunks(query, index, ids, vector_log, chunk_traces, store_type=STORE_CHOICE)

        # 4. Print results
        print(f"\n--- Top {len(retrieved_data)} results for query: '{query}' ---")
        for i, item in enumerate(retrieved_data, 1):
            print(f"\n--- Result {i} ---")
            print(f"File: {item['file_name']}")
            print(f"Chunk ID: {item['chunk_id']}")
            print(f"Similarity Distance: {item['similarity_distance']:.4f}")
            print(f"Text: {item['chunk_text'][:300]}...") # Preview of the chunk text

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
