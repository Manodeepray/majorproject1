# Project Overview

This document provides a high-level overview of the project's architecture, components, and data flow, based on an analysis of the source code.

## 1. High-Level Architecture

The project is a sophisticated Knowledge Base API built on a microservices-style architecture, even though it's deployed as a single application. It consists of two main FastAPI servers:

1.  **Main API Server (`src/server.py`):** This is the primary user-facing entry point. It handles file uploads, user queries, and requests for generative content (summaries, quizzes, etc.). It orchestrates the various pipelines and interacts with the Inference Server for AI-powered tasks.
2.  **Inference Server (`src/InferenceServer.py`):** This server is a dedicated backend for running AI models. It exposes endpoints for generating text and performing inference, abstracting the underlying model implementations (local Llama.cpp models and the Groq API).

The system is designed around a data pipeline that ingests unstructured documents, processes them into a searchable format, and then uses this knowledge base to answer queries and generate new content.

## 2. Core Components and Modules

### 2.1. Main API Server (`src/server.py`)

-   **Framework:** FastAPI.
-   **Responsibilities:**
    -   Provides RESTful endpoints for all user interactions: `/upload`, `/query`, `/deepquery`, `/summarize`, `/generate_faq`, etc.
    -   Manages background tasks for processing uploaded files.
    -   Loads and holds the vector store indexes and logs in memory for quick retrieval.
    -   Handles file and data management, including status tracking and deletion.

### 2.2. Data Ingestion and Processing

-   **`src/DataCollectionPipe.py`**: The master script that orchestrates the entire data ingestion process. It calls the ingestion pipeline and then triggers the building of vector store indexes.
-   **`src/dataIngestion/` (Directory)**: Contains the logic for processing raw documents, chunking them, and preparing them for vectorization. (Note: The specific files in this directory were not reviewed, but their function is clear from the pipeline).

### 2.3. Retrieval Pipeline

-   **`src/retrieverPipeline.py`**: Manages the core retrieval logic. It loads the vector stores (FAISS and HNSW) and associated logs. Its `retrieve_chunks` function is the central point for searching the knowledge base.
-   **`src/retriever/` (Directory)**: Contains the specific implementations for creating, saving, and loading FAISS and HNSW vector stores.

### 2.4. Query Processing and Agents

-   **`src/promptAgent.py`**: Implements the `MultiTurnAgent` for the `/deepquery` endpoint. This agent is responsible for:
    1.  Breaking down a complex user query into simpler sub-queries.
    2.  Retrieving relevant context for each sub-query.
    3.  Summarizing the context for each sub-query.
    4.  Synthesizing a final, comprehensive answer from the intermediate summaries.
    5.  Optionally, triggering knowledge graph creation from the retrieved context.

### 2.5. Generative Content Engine

-   **`src/generative/engine.py`**: The central orchestrator for all generative tasks (summaries, outlines, FAQs, quizzes, flashcards).
    -   It reads the content of processed documents from the data warehouse.
    -   It splits the content into manageable chunks.
    -   It calls the appropriate generative function for each chunk concurrently using `asyncio`.
    -   It aggregates the results from the chunks to produce the final output.
-   **`src/generative/*.py`**: Each file (`summarize.py`, `quiz.py`, etc.) contains the specific logic for making calls to the Inference Server with the correct prompts to generate a particular type of content. They also include helpers for parsing the model's output (e.g., `extract_json_from_text`).

### 2.6. Knowledge Graph Pipeline

-   **`src/knowledgeGraphPipeline.py`**: Provides functions to create knowledge graphs.
    -   `createDatabaseKnowledgeGraph()`: Builds a graph from all the processed data in the database.
    -   `create_knowledge_graph_from_context()`: Generates a smaller, on-the-fly graph from the context retrieved during a `/deepquery` call.
-   **`src/knowledgeGraph/entity_relation_extraction.py`**: Uses the `kg-gen` library with a Gemini model to perform the core entity and relation extraction from text. It handles loading previous data and merging it with newly extracted information.

### 2.7. Inference Server & Processors

-   **`src/InferenceServer.py`**: A FastAPI server dedicated to running the AI models. It is well-instrumented with logging, metrics (Prometheus), and tracing (Jaeger).
-   **`src/inference/processor.py`**: Contains the model abstraction layer.
    -   `FastProcessor`: Uses a smaller, local `Qwen` model via `llama-cpp` for tasks like entity recognition or simple summarization.
    -   `LargeProcessor`: Uses the powerful `llama-3.3-70b-versatile` model via the Groq API for more demanding tasks like agentic reasoning, query decomposition, and final answer generation.

### 2.8. Database and File Management

-   **`src/database.py`**: Contains utility functions for managing the file-based "database" of the application. The `delete_files_from_db` function is a critical piece of this, ensuring that when a file is deleted, all its associated chunks, logs, and vector embeddings are properly purged.
-   **`database/` (Directory)**: Acts as the central data store, containing:
    -   `data_warehouse/`: The original uploaded documents.
    -   `processed/`: Cleaned and chunked text.
    -   `vectordb/`: The raw vector embedding files (`.npy`).
    -   `logs/`: JSON files that act as metadata indexes (`file_status.json`, `chunk_traces.json`, `vector_log.json`).

## 3. Data Flow

1.  **Upload:** A user uploads one or more documents to the `/upload` endpoint.
2.  **Ingestion:** A background task is triggered. The `DataCollectionPipe` runs, processing the documents into text chunks and creating vector embeddings for each chunk.
3.  **Indexing:** The pipeline then uses the generated vectors to build and save FAISS and HNSW indexes for fast retrieval. All metadata is updated in the `database/logs/` JSON files.
4.  **Query:**
    -   A user sends a question to the `/query` or `/deepquery` endpoint.
    -   The `retrieverPipeline` uses the vector indexes to find the most relevant text chunks.
    -   The query and the context from the chunks are sent to the `InferenceServer`.
    -   The `LargeProcessor` (Groq API) generates a final answer.
    -   For a `/deepquery`, the `MultiTurnAgent` first breaks the query down, retrieves context for each part, summarizes it, and then generates the final answer.
5.  **Generation:**
    -   A user requests to generate content (e.g., a quiz) for specific files via an endpoint like `/generate_quiz`.
    -   The `generative/engine.py` reads the content of the requested files.
    -   It sends the content in chunks to the `InferenceServer` with a specialized prompt.
    -   The `InferenceServer` generates the content (e.g., JSON for a quiz).
    -   The main server parses the response and returns it to the user.
