import os
import json
import shutil
from pathlib import Path
from typing import List

# Define paths
project_root = Path(__file__).parent.parent
LOGS_DIR = project_root / "database" / "logs"
DATA_WAREHOUSE_DIR = project_root / "database" / "data_warehouse"
VECTORDB_DIR = project_root / "database" / "vectordb"
PROCESSED_CHUNKS_DIR = project_root / "database" / "processed" / "chunks"


def load_json(path):
    if path.exists():
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {} # Return empty dict if file is empty or malformed
    return {}

def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def delete_files_from_db(filenames: List[str]):
    """
    Deletes files and their associated data from the database.
    """
    file_status_path = LOGS_DIR / "file_status.json"
    chunk_status_path = LOGS_DIR / "chunk_status.json"
    chunk_traces_path = LOGS_DIR / "chunk_traces.json"
    vector_log_path = LOGS_DIR / "vector_log.json"

    file_status = load_json(file_status_path)
    chunk_status = load_json(chunk_status_path)
    chunk_traces = load_json(chunk_traces_path)
    vector_log = load_json(vector_log_path)

    deleted_files_count = 0
    errors = []

    for filename in filenames:
        try:
            # 1. Mark as deleted in file_status.json
            if filename in file_status:
                file_status[filename]['status'] = 'deleted'
                file_status[filename]['deleted'] = True

            # 2. Delete from data_warehouse
            file_to_delete = DATA_WAREHOUSE_DIR / filename
            if file_to_delete.exists():
                file_to_delete.unlink()

            # 3. Delete chunk directory and update chunk_status.json
            if filename in chunk_status:
                if chunk_status[filename].get('chunks'):
                    first_chunk_path_str = chunk_status[filename]['chunks'][0].get('chunk_path')
                    if first_chunk_path_str:
                        chunk_directory = project_root / Path(first_chunk_path_str).parent
                        if chunk_directory.exists() and chunk_directory.is_dir():
                            shutil.rmtree(chunk_directory)
                del chunk_status[filename]

            # 4. Delete from chunk_traces.json
            chunk_traces = {
                k: v for k, v in chunk_traces.items() if v.get('file_name') != filename
            }

            # 5. Delete vectors from vector_log.json and .npy files
            vector_ids_to_delete = [
                vec_id for vec_id, vec_data in vector_log.items() if vec_data.get('file_name') == filename
            ]
            
            for vec_id in vector_ids_to_delete:
                vec_data = vector_log.pop(vec_id, None)
                if vec_data and 'embedding_path' in vec_data:
                    embedding_path = Path(vec_data['embedding_path'])
                    if embedding_path.exists():
                        embedding_path.unlink()

            deleted_files_count += 1

        except Exception as e:
            errors.append({"filename": filename, "error": str(e)})

    # Save updated JSON files
    save_json(file_status, file_status_path)
    save_json(chunk_status, chunk_status_path)
    save_json(chunk_traces, chunk_traces_path)
    save_json(vector_log, vector_log_path)

    return {"deleted_count": deleted_files_count, "errors": errors}