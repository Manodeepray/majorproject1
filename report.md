# 📚 Voice-Driven Learning Assistant Using LLMs and Knowledge Graphs and Vectorstore: Project Document

This document provides a detailed overview of the **Voice-Driven Learning Assistant** project, outlining its current features and future development plans.

---

## 🌟 Project Title and Core Concept

**Title:** Voice-Driven Learning Assistant Using LLMs and Knowledge Graphs and Vectorstore

**Core Concept:** A sophisticated, modular learning system that utilizes **Large Language Models (LLMs)** and a dynamic **Knowledge Graph (KG)**, backed by a custom, traceable **vector database** infrastructure, all accessible through a **voice interface**. The initial prototype was similar to **notebook-based learning system**.

---

## ⚙️ Data and Vector Infrastructure

### Custom Data and Vector Pipeline

The entire data ingestion and vector database system was built **from scratch** to ensure maximum control, flexibility, and performance.

* **Data Ingestion Pipeline:** Custom-built to process and prepare data for the vector store.
* **Vector Database Implementation:** Custom-built for tailored indexing and retrieval.
* **Embeddings Model:** Utilizes a **Sentence Transformer** for generating high-quality vector representations (embeddings) of the data chunks.
* **Vector Store Technology:** Combines **FAISS** (for efficient similarity search) and **HNSW** (Hierarchical Navigable Small World, for state-of-the-art approximate nearest neighbor search) for robust retrieval.
* **Chunking Strategy:** Implements **chunk tracing** to map embeddings back to their original document segments.

### **Scalability and Efficiency**

The architecture is designed for seamless, continuous operation:

* **Free Expandability:** The vector databases and chunk databases are designed to be **freely expandable** to accommodate growing data volumes.
* **Incremental Processing:** The system intelligently avoids reprocessing: it **does not need to re-chunk everything** or **re-vectorize already processed data**, ensuring efficiency during updates and expansion.

### **Tracking and Auditing**

Comprehensive logging and tracking are integrated for monitoring and debugging:

* **Logging:** General system and process logging.
* **Vector Tracing:** Detailed tracing of vector operations and retrieval paths.
* **Chunk Tracing:** Tracking of data chunking process and mapping.
* **Data Warehouse:** A data warehouse is maintained for tracking processed data, including support for **soft deletion** of content.

---

## 💻 Inference and Model Architecture

The system uses a two-tiered LLM approach, served via an **FastAPI inference server**.

### **Inference Server (FastAPI)**

* A high-performance **FastAPI** server is deployed to handle all API requests, model inference, and query processing.

### **LLM Utilization**

1.  **Small LLM (Knowledge Graph/Entity Processing):**
    * Uses a small, efficient model running via **Llama-CPP ($\text{llama.cpp}$)**.
    * **Purpose:** Dedicated to tasks requiring rapid, local processing, such as **knowledge graph creation** and **entity extraction**.
2.  **Larger LLM (Query Answering/Generation):**
    * Leverages the **Groq API** for faster inference with a larger, more capable model.
    * **Purpose:** Handles complex tasks like **query answering**, **deep query compilation**, and content **generation (summaries, quizzes, etc.)**.

---

## 🧠 Knowledge Graph Pipeline

A key feature of the system is its ability to create a dynamic, content-driven knowledge graph.

* **Knowledge Graph Pipeline:** This dedicated pipeline takes the **retrieved information** from the vector store search and processes it to construct a **dynamic Knowledge Graph** in real-time.
* **Dynamic Creation:** The KG is generated based on the specific context of the retrieved documents, making it highly relevant to the current learning session or query.

---

## 🔎 Query and Retrieval System

The system offers two modes of querying to address different user needs:

### **1. Standard Query**

* **Process:** The user's query is vectorized, and the system **retrieves the top $k$ relevant documents** from the combined **FAISS + HNSW** vector stores.
* **Output:** The LLM uses the retrieved context to formulate a concise answer.

### **2. Deep Query**

* **Purpose:** Designed for more complex questions requiring a comprehensive answer from multiple sources.
* **Process:**
    1.  The initial query is broken down into **several smaller sub-queries**.
    2.  For **each sub-query**, the system performs a separate retrieval, fetching the **top $k$ documents** from the vector stores.
    3.  The LLM then **compiles** the context from all retrieved sub-query results to formulate a deeper, more detailed answer.
* **Knowledge Graph Option:** Includes a **flag option** to automatically trigger the **Knowledge Graph pipeline** if the user requires a visual/structured representation of the deep query's findings.

---

## 📝 Document Processing and Generation Features

For any **selected document or set of retrieved documents**, the system can perform various generative tasks:

| Feature | Description |
| :--- | :--- |
| **Generate Summaries** | Creates a concise overview of the document's content. |
| **Generate FAQ** | Creates a list of **Frequently Asked Questions** based on the document's key points. |
| **Generate Quizzes** | Creates learning assessments, including **Multiple-Choice Questions (MCQ)** or **short-answer questions**. |
| **Generate Flash Cards** | Creates question/answer pairs for spaced repetition and memory testing. |
| **Generate Outline** | Creates a structured, hierarchical outline of the document's main topics and sub-points. |

---

## 🚀 Future Development - To Do

The next phase of the project will focus on user experience, system architecture, and personalization.

* **Voice Interface:** **Everything will have a voice interface**, making the assistant fully hands-free and conversational.
* **Multi-User Experience:** Developing features and architecture to support a **multi-user experience**.
* **Customizable Knowledge Graph:** Allowing users to **customize** how the Knowledge Graph is created, viewed, and interacted with.
* **System Design for Scaling:** Implementing **system design concepts** to ensure the platform can **host multiple users at once** with robust performance and reliability.

Would you like to focus on the **system design concepts for multi-user hosting** or perhaps detail the **architecture of the voice interface**?