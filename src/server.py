import os
import shutil
from pathlib import Path
from typing import List
import httpx
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Body
from pydantic import BaseModel, Field
import uvicorn

# Add project root to Python path to allow for absolute imports
project_root = Path(__file__).parent.parent
import sys
sys.path.append(str(project_root))

from src.DataCollectionPipe import run_pipe
from src.retrieverPipeline import load_logs, load_vector_store, retrieve_chunks
from src.knowledgeGraphPipeline import createDatabaseKnowledgeGraph
from src.promptAgent import MultiTurnAgent

# --- Configuration ---
# Directories
UPLOAD_DIR = project_root / "uploaded"
DATA_WAREHOUSE_DIR = project_root / "database" / "data_warehouse"

# Server
INFERENCE_SERVER_URL = "http://127.0.0.1:8000/infer"

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Knowledge Base API",
    description="""
A comprehensive API for building and querying a knowledge base from unstructured documents.

**Workflow:**
1.  **Upload Documents:** Use the `/upload` endpoint to submit your files (.txt, .pdf, etc.). The server will process them in the background to build a searchable vector index.
2.  **Query the Knowledge Base:** Once processing is complete, use the `/query` endpoint to ask questions. The API will retrieve relevant information and generate a concise answer.
""",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# --- Global Variables ---
# These will be loaded at startup and reused across requests
app.state.vector_log = None
app.state.chunk_traces = None
app.state.index = None
app.state.ids = None
app.state.store_type = 'hnsw'  # or 'faiss'

# --- Pydantic Models ---
class QueryRequest(BaseModel):
    """Request model for the /query endpoint."""
    query: str = Field(
        ...,
        description="The natural language question you want to ask the knowledge base.",
        example="What are the main findings of the research paper?"
    )
    top_k: int = Field(
        20,
        description="The number of relevant document chunks to retrieve for context.",
        example=10
    )

class QueryResponse(BaseModel):
    """Response model for the /query endpoint."""
    answer: str = Field(
        ...,
        description="The generated answer from the language model.",
        example="The main findings indicate a significant correlation between..."
    )
    context: List[str] = Field(
        ...,
        description="The list of document chunks used as context to generate the answer.",
        example=[
            "Chunk 1 text...",
            "Chunk 2 text..."
        ]
    )

# --- Background Tasks ---
def run_data_pipeline():
    """
    Wrapper function to run the data ingestion and indexing pipeline.
    """
    print("Starting data ingestion and indexing pipeline in the background...")
    try:
        # Before running the pipe, move uploaded files to the data warehouse
        if not DATA_WAREHOUSE_DIR.exists():
            DATA_WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
        
        for filename in os.listdir(UPLOAD_DIR):
            shutil.move(str(UPLOAD_DIR / filename), str(DATA_WAREHOUSE_DIR / filename))
            print(f"Moved {filename} to data warehouse.")

        run_pipe()
        print("Data pipeline finished successfully.")
        # After pipeline runs, reload the vector stores for the main app
        load_retriever_assets()
        print("Retriever assets reloaded.")

    except Exception as e:
        print(f"Error during data pipeline execution: {e}")

# --- Server Events ---
@app.on_event("startup")
def startup_event():
    """
    Load retriever assets on server startup.
    """
    print("Server starting up...")
    load_retriever_assets()

def load_retriever_assets():
    """
    Loads logs and the vector store index.
    """
    try:
        app.state.vector_log, app.state.chunk_traces = load_logs()
        app.state.index, app.state.ids = load_vector_store(store_type=app.state.store_type)
        print(f"✅ Successfully loaded logs and '{app.state.store_type}' vector store.")
    except FileNotFoundError:
        print("⚠️ Warning: Log files or vector store not found. Please upload files to build them.")
    except Exception as e:
        print(f"An unexpected error occurred while loading retriever assets: {e}")

# --- API Endpoints ---
@app.post(
    "/upload",
    summary="Upload documents to the knowledge base",
    description="Upload a list of files to be processed and indexed. This operation runs in the background and may take some time depending on the size and number of documents.",
    responses={
        200: {
            "description": "Files uploaded successfully and processing started.",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Files ['document1.pdf', 'notes.txt'] uploaded successfully. Processing started in the background.",
                        "detail": "The data ingestion and indexing pipeline is running. You can query the data once it's complete."
                    }
                }
            }
        }
    }
)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    Handles file uploads, saves them, and triggers the data processing pipeline
    in the background.

    The processing pipeline includes:
    1. Ingesting and chunking the documents.
    2. Creating vector embeddings.
    3. Building FAISS and HNSW vector indexes for retrieval.
    """
    # Create upload directory if it doesn't exist
    UPLOAD_DIR.mkdir(exist_ok=True)

    saved_files = []
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file.filename)

    # Run the pipeline in the background
    background_tasks.add_task(run_data_pipeline)
    # background_tasks.add_task(createDatabaseKnowledgeGraph)
    return {
        "message": f"Files {saved_files} uploaded successfully. Processing started in the background.",
        "detail": "The data ingestion and indexing pipeline is running. You can query the data once it's complete."
    }

@app.post(
    "/query",
    response_model=QueryResponse,
    summary="Query the knowledge base",
    description="Ask a question and get an answer based on the documents you've uploaded. This endpoint retrieves relevant context from the indexed data and uses a language model to generate a response.",
    responses={
        404: {"description": "No relevant documents found."},
        503: {"description": "Vector store is not available. Upload documents first."}
    }
)
async def query_knowledge_base(
    request: QueryRequest = Body(
        ...,
        example={
            "query": "What is the impact of climate change on marine ecosystems?",
            "top_k": 5
        }
    )
):
    """
    Queries the document base by:
    1. Breaking down the query into sub-queries.
    2. Retrieving and summarizing context for each sub-query.
    3. Generating a final answer based on the collected information.
    """
    if app.state.index is None or app.state.ids is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store is not available. Please upload documents first."
        )

    try:
        agent = MultiTurnAgent(
            index=app.state.index,
            ids=app.state.ids,
            vector_log=app.state.vector_log,
            chunk_traces=app.state.chunk_traces,
            store_type=app.state.store_type
        )
        
        result = await agent.run(query=request.query, top_k=request.top_k)
        
        if not result["context"]:
            raise HTTPException(status_code=404, detail="No relevant documents found for your query.")

        return result

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to inference server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during query: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

# --- Main Execution ---
if __name__ == "__main__":
    # Note: The inference server in `InferenceServer.py` should be running on port 8000.
    # This main server will run on port 8001.
    uvicorn.run(app, host="0.0.0.0", port=8001)
