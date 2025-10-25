import json

def load_chunk_text(chunk_path):
    """Safely load a chunk's text content."""
    try:
        with open(chunk_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error reading chunk: {chunk_path} → {e}")
        return ""


def retrieve_chunks_from_results(similarity_results, vector_log, chunk_traces):
    """
    Retrieve original chunk text and metadata using vector IDs.
    """
    retrieved_chunks = []

    for result in similarity_results:
        vector_id = result["vector_id"]

        if vector_id not in vector_log:
            print(f"⚠️ Missing vector_id in log: {vector_id}")
            continue

        log_entry = vector_log[vector_id]
        chunk_path = log_entry["chunk_path"]
        file_name = log_entry["file_name"]
        chunk_id = log_entry["chunk_id"]
        metadata = log_entry["metadata"]

        # Load chunk text
        text = load_chunk_text(chunk_path)

        # Add to result set
        retrieved_chunks.append({
            "vector_id": vector_id,
            "file_name": file_name,
            "chunk_id": chunk_id,
            "chunk_path": chunk_path,
            "metadata": metadata,
            "similarity_distance": result.get("distance"),
            "chunk_text": text
        })

    return retrieved_chunks
