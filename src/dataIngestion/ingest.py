# ============================================================
# 📦 Data Ingestion Pipeline — Starter Notebook
# Author: Manodeep Ray
# Date: 2025-10-14
# ============================================================

import os
import shutil
import json
import hashlib
from datetime import datetime
import pandas as pd
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader
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
# 3️⃣ Helper Functions
# ------------------------------------------------------------
def compute_file_hash(file_path):
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def log_message(message, PROCESS_LOG):
    """Log messages with timestamp."""
    timestamp = datetime.utcnow().isoformat()
    with open(PROCESS_LOG, "a") as log:
        log.write(f"[{timestamp}] {message}\n")
    print(message)

def load_status(STATUS_FILE):
    """Load status JSON."""
    with open(STATUS_FILE, "r") as f:
        return json.load(f)

def save_status(status_data, STATUS_FILE):
    """Save updated status JSON."""
    print(STATUS_FILE , status_data)
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

# ------------------------------------------------------------
# 4️⃣ File Reading (Simple Preview Functionality)
# ------------------------------------------------------------
def read_file(file_path, PROCESS_LOG):
    """Read text from TXT, DOCX, or PDF."""
    ext = file_path.suffix.lower()
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:
            return None
    except Exception as e:
        log_message(f"\n{Colors.RED}[ERROR]{Colors.RESET} Error reading file {file_path.name}: {e}", PROCESS_LOG)
        return None

# ------------------------------------------------------------
# 5️⃣ Main Ingestion Function
# ------------------------------------------------------------
def ingest_files(UPLOADED_DIR, DATA_WAREHOUSE_DIR, LOG_DIR):
    """
    Ingests files from UPLOADED_DIR to DATA_WAREHOUSE_DIR and logs the process.
    """
    STATUS_FILE = LOG_DIR / "file_status.json"
    PROCESSED_CSV = LOG_DIR / "processed_files.csv"
    PROCESS_LOG = LOG_DIR / "processing_log.txt"

    # Initialize files if not exist
    if not STATUS_FILE.exists():
        with open(STATUS_FILE, "w") as f:
            json.dump({}, f, indent=4)
        status_data = {}
    else:
        status_data = load_status(STATUS_FILE)
        
        
        
    if not PROCESSED_CSV.exists():
        pd.DataFrame(columns=["file_name", "status", "timestamp", "hash"]).to_csv(PROCESSED_CSV, index=False)

    

    for file_path in tqdm(UPLOADED_DIR.glob("*.*") , desc="Processing..."):
        file_name = file_path.name
        file_hash = compute_file_hash(file_path)
        timestamp = datetime.utcnow().isoformat()

        
        
        status_data[file_name] = {
            "hash":None,
            "status": None,
            "timestamp":None,
        }
        # Skip if already processed and hash unchanged
        if file_name in status_data and status_data[file_name]["hash"] == file_hash:
            log_message(f"\n{Colors.RED}[ALERT]{Colors.RESET} File {file_name} already processed — skipping.", PROCESS_LOG)
            continue

        # Try reading and moving file
        text_data = read_file(file_path, PROCESS_LOG)
        if text_data is None:
            status_data[file_name] = {"status": "failed", "timestamp": timestamp, "hash": file_hash}
            log_message(f"\n{Colors.RED}[ERROR]{Colors.RESET} Failed to process {file_name}", PROCESS_LOG)
            continue

        try:
            # Move to data warehouse
            dest_path = DATA_WAREHOUSE_DIR / file_name
            shutil.move(str(file_path), str(dest_path))

            # Update status
            status_data[file_name] = {"status": "pending", "timestamp": timestamp, "hash": file_hash}
            log_message(f"\n{Colors.GREEN}[SUCCESS]{Colors.RESET} Processed and moved {file_name} to data warehouse.", PROCESS_LOG)

        except Exception as e:
            status_data[file_name] = {"status": "failed", "timestamp": timestamp, "hash": file_hash}
            log_message(f"\n{Colors.RED}[ERROR]{Colors.RESET} Error moving file {file_name}: {e}", PROCESS_LOG)

    # Save status JSON
    save_status(status_data, STATUS_FILE)

    # Update CSV
    df = pd.DataFrame([
        {"file_name": k, "status": v["status"], "timestamp": v["timestamp"], "hash": v["hash"]}
        for k, v in status_data.items()
    ])
    print(df)
    df.to_csv(PROCESSED_CSV, index=False)

    # breakpoint()
        
