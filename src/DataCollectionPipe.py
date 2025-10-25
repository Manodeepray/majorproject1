from src.dataIngestion.status import run_ingestion_pipeline
from src.retriever.faiss_vector_store import build_faiss_index
from src.retriever.hnsw_vector_store import build_hnsw_index
import json
import os


def run_pipe():
    run_ingestion_pipeline()

    VECTOR_LOG_PATH = "database/logs/vector_log.json"
    
    if not os.path.exists(VECTOR_LOG_PATH):
        print(f"Vector log not found at {VECTOR_LOG_PATH}, cannot build indexes.")

    else:
        with open(VECTOR_LOG_PATH, "r") as f:
            vector_log = json.load(f)

        print("Building FAISS index...")
        build_faiss_index(vector_log)

        print("Building HNSW index...")
        build_hnsw_index(vector_log)
    
    pass


if __name__ == "__main__":
    run_ingestion_pipeline()

    VECTOR_LOG_PATH = "database/logs/vector_log.json"
    
    if not os.path.exists(VECTOR_LOG_PATH):
        print(f"Vector log not found at {VECTOR_LOG_PATH}, cannot build indexes.")

    else:
        with open(VECTOR_LOG_PATH, "r") as f:
            vector_log = json.load(f)

        print("Building FAISS index...")
        build_faiss_index(vector_log)

        print("Building HNSW index...")
        build_hnsw_index(vector_log)