# ============================================================
# 🧩 Cleaning + Chunking + Metadata Tracking (RAG-Ready)
# Author: Manodeep Ray
# ============================================================

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from PyPDF2 import PdfReader
from docx import Document
from tqdm import tqdm




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


# ------------------------------------------------------------
# 🧹 Cleaning Function
# ------------------------------------------------------------
def clean_text(text):
    """Clean and standardize extracted text."""
    if not isinstance(text, str):
        return ""
    
    text = text.encode("ascii", "ignore").decode()                  # Remove non-ASCII
    text = re.sub(r"http\S+|www\S+|https\S+", "[URL]", text)        # Replace URLs
    text = re.sub(r"[^a-zA-Z0-9.,;:?!()\[\]'\s-]", " ", text)      # Remove unwanted chars
    text = re.sub(r"\s+", " ", text).strip()                        # Normalize whitespace
    text = text.lower()                                             # Normalize case
    return text

# ------------------------------------------------------------
# 📄 File Reading with Page Extraction (for PDFs)
# ------------------------------------------------------------
def read_file_content_with_pages(file_path):
    """Extracts text by pages if PDF, else as single document."""
    ext = file_path.suffix.lower()
    try:
        if ext == ".pdf":
            reader = PdfReader(file_path)
            return [(i + 1, page.extract_text()) for i, page in enumerate(reader.pages) if page.extract_text()]
        elif ext == ".docx":
            doc = Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
            return [(None, text)]
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return [(None, f.read())]
        else:
            return []
    except Exception as e:
        print(f"⚠️ Error reading {file_path.name}: {e}")
        return []

# ------------------------------------------------------------
# 🧩 Chunking Function
# ------------------------------------------------------------
def chunk_text(text, chunk_size=800, overlap=100):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# ------------------------------------------------------------
# 🔑 Hash & JSON Utilities
# ------------------------------------------------------------
def compute_file_hash(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def load_chunk_status(CHUNK_STATUS_FILE):
    with open(CHUNK_STATUS_FILE, "r") as f:
        return json.load(f)

def save_chunk_status(data, CHUNK_STATUS_FILE):
    with open(CHUNK_STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------------------------------------------
# 🚀 Main Process
# ------------------------------------------------------------
def process_data_warehouse_with_metadata(DATA_WAREHOUSE_DIR, CLEANED_DIR, CHUNK_DIR, LOG_DIR, chunk_size=500, overlap=100):
    BASE_DIR = Path.cwd()
    CHUNK_STATUS_FILE = LOG_DIR / "chunk_status.json"
    if not CHUNK_STATUS_FILE.exists():
        with open(CHUNK_STATUS_FILE, "w") as f:
            json.dump({}, f, indent=4)

    chunk_status = load_chunk_status(CHUNK_STATUS_FILE)

    for file_path in tqdm(DATA_WAREHOUSE_DIR.glob("*.*") , desc="processing..."):
        if file_path.name not in chunk_status:
            print(f"\n{Colors.YELLOW}[LOG]{Colors.RESET} Processing {file_path.name} ...")
            file_hash = compute_file_hash(file_path)
            timestamp = datetime.utcnow().isoformat()

            # Extract text (with page numbers)
            pages = read_file_content_with_pages(file_path)
            if not pages:
                print(f"\n{Colors.RED}[ERROR]  No readable text found in {Colors.RESET}{file_path.name}")
                continue

            all_chunk_metadata = []
            cleaned_file = CLEANED_DIR / f"{file_path.stem}_cleaned.txt"

            # Process each page
            with open(cleaned_file, "w", encoding="utf-8") as cf:
                for page_number, page_text in pages:
                    if not page_text:
                        continue

                    cleaned_text = clean_text(page_text)
                    cf.write(cleaned_text + "\n\n")

                    # Chunk per page
                    chunks = chunk_text(cleaned_text, chunk_size, overlap)
                    chunk_folder = CHUNK_DIR / file_path.stem
                    chunk_folder.mkdir(parents=True, exist_ok=True)

                    for i, chunk in enumerate(chunks, start=1):
                        chunk_file = chunk_folder / f"{file_path.stem}_page{page_number or 0}_chunk_{i}.txt"
                        with open(chunk_file, "w", encoding="utf-8") as f:
                            f.write(chunk)

                        # Metadata for retrieval / vector DB
                        all_chunk_metadata.append({
                            "chunk_id": len(all_chunk_metadata) + 1,
                            "file_name": file_path.name,
                            "source": str(file_path.relative_to(BASE_DIR)),
                            "chunk_file": chunk_file.name,
                            "chunk_path": str(chunk_file.relative_to(BASE_DIR)),
                            "page_number": page_number,
                            "chunk_length": len(chunk.split()),
                            "hash": file_hash,
                            "timestamp": timestamp,
                            "processed": False,
                            "er_extraction":False,
                            "vectorized":False,
                        })

            # Record metadata
            chunk_status[file_path.name] = {
                "status": "chunked",
                "timestamp": timestamp,
                "hash": file_hash,
                "chunks": all_chunk_metadata,
                "status": "pending"
            }

            print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {len(all_chunk_metadata)} chunks created with metadata for {file_path.name}")

    save_chunk_status(chunk_status, CHUNK_STATUS_FILE)
    print(f"\n{Colors.BLUE}[LOG]{Colors.RESET}   Updated chunk_status.json")

def trace_chunks(LOG_DIR):
    import json
    import os

    # Paths
    CHUNKS_STATUS_PATH = LOG_DIR / "chunk_status.json"
    CHUNK_TRACES_PATH = LOG_DIR / "chunk_traces.json"

    # --- 1. Load existing chunk status ---
    if not os.path.exists(CHUNKS_STATUS_PATH):
        raise FileNotFoundError(F"{Colors.RED}[ERROR]{Colors.RESET}   chunks_status.json not found. Please run the chunking step first.")

    with open(CHUNKS_STATUS_PATH, "r") as f:
        chunks_status = json.load(f)

    # --- 2. Load existing chunk traces (if available) ---
    if os.path.exists(CHUNK_TRACES_PATH):
        with open(CHUNK_TRACES_PATH, "r") as f:
            chunk_traces = json.load(f)
    else:
        chunk_traces = {}

    # --- 3. Create or update flat trace dictionary ---
    new_traces = 0

    for file_name, info in chunks_status.items():
        if "chunks" in info and isinstance(info["chunks"], list):
            for chunk in info["chunks"]:
                trace_id = f"{file_name}_chunk_{chunk['chunk_id']}"
                if trace_id not in chunk_traces:  # only add if new
                    chunk_traces[trace_id] = {
                        "file_name": chunk["file_name"],
                        "chunk_id": chunk["chunk_id"],
                        "source": chunk["source"],
                        "chunk_file": chunk["chunk_file"],
                        "chunk_path": chunk["chunk_path"],
                        "page_number": chunk["page_number"],
                        "chunk_length": chunk["chunk_length"],
                        "timestamp": chunk["timestamp"],
                        "hash": chunk["hash"],
                        "vectorized": False
                    }
                    new_traces += 1

    # --- 4. Save merged trace dictionary ---
    os.makedirs(os.path.dirname(CHUNK_TRACES_PATH), exist_ok=True)
    with open(CHUNK_TRACES_PATH, "w") as f:
        json.dump(chunk_traces, f, indent=4)

    # --- 5. Summary ---
    print(f"\n{Colors.GREEN}[SUCCESS]{Colors.RESET} Chunk trace file updated successfully: {CHUNK_TRACES_PATH}")
    print(f"Total chunks tracked: {len(chunk_traces)}")
    print(f"\n{Colors.YELLOW}[LOG]{Colors.RESET}  New traces added: {new_traces}")


