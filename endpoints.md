# API Endpoints Documentation

This document provides a detailed overview of the API endpoints available in the Knowledge Base API.

## Table of Contents

- [Health Check](#health-check)
- [File Status](#file-status)
- [Upload Files](#upload-files)
- [Query Knowledge Base](#query-knowledge-base)
- [Deep Query Knowledge Base](#deep-query-knowledge-base)
- [Generate Outline](#generate-outline)
- [Summarize Documents](#summarize-documents)
- [Generate FAQ](#generate-faq)
- [Generate Quiz](#generate-quiz)
- [Generate Flashcards](#generate-flashcards)
- [Delete Files](#delete-files)

---

## Health Check

- **Endpoint:** `GET /health`
- **Summary:** Checks the health status of the API.
- **Input:** None
- **Output:**
  - `200 OK`:
    ```json
    {
      "status": "healthy"
    }
    ```

---

## File Status

- **Endpoint:** `GET /file_status`
- **Summary:** Get the processing status of all uploaded files.
- **Input:** None
- **Output:**
  - `200 OK`: A JSON object detailing the processing status of each file.
    ```json
    {
      "document1.pdf": {
        "status": "processed",
        "timestamp": "2023-10-27T10:00:00Z"
      },
      "notes.txt": {
        "status": "pending",
        "timestamp": "2023-10-27T10:05:00Z"
      },
      "report.docx": {
        "status": "error",
        "message": "Failed to parse document."
      }
    }
    ```
  - `404 Not Found`: If the file status log does not exist.

---

## Upload Files

- **Endpoint:** `POST /upload`
- **Summary:** Upload documents to the knowledge base for processing.
- **Input:**
  - `files`: A list of files to upload (e.g., PDF, TXT).
- **Output:**
  - `200 OK`:
    ```json
    {
      "message": "Files ['document1.pdf', 'notes.txt'] uploaded successfully. Processing started in the background.",
      "detail": "The data ingestion and indexing pipeline is running. You can query the data once it's complete."
    }
    ```

---

## Query Knowledge Base

- **Endpoint:** `POST /query`
- **Summary:** Query the knowledge base with a direct question.
- **Input:**
  ```json
  {
    "query": "What is the impact of climate change on marine ecosystems?",
    "top_k": 5
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "answer": "The main findings indicate a significant correlation between X and Y, suggesting Z.",
      "context": [
        "Relevant chunk 1 text...",
        "Relevant chunk 2 text..."
      ]
    }
    ```
  - `404 Not Found`: No relevant documents found for the query.
  - `503 Service Unavailable`: Vector store is not available.
  - `500 Internal Server Error`: Internal server error or inference server connection issue.

---

## Deep Query Knowledge Base

- **Endpoint:** `POST /deepquery`
- **Summary:** Perform a multi-turn, in-depth query on the knowledge base.
- **Input:**
  ```json
  {
    "query": "What is the impact of climate change on marine ecosystems, and what are the proposed solutions?",
    "top_k": 5,
    "create_graph": true
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "answer": "The impact of climate change on marine ecosystems is severe, leading to... Proposed solutions include...",
      "context": [
        "Summarized chunk for sub-query 1...",
        "Summarized chunk for sub-query 2..."
      ],
      "sub_queries": [
        "Impact of climate change on marine ecosystems",
        "Proposed solutions for climate change in marine environments"
      ],
      "graph_location": "/path/to/generated_knowledge_graph.html"
    }
    ```
  - `404 Not Found`: No relevant documents found for the query.
  - `503 Service Unavailable`: Vector store is not available.
  - `500 Internal Server Error`: Internal server error or inference server connection issue.

---

## Generate Outline

- **Endpoint:** `POST /generate_outline`
- **Summary:** Generate hierarchical outlines for documents.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"],
    "combine": false
  }
  ```
- **Output:**
  - `200 OK`:
    - If `combine` is `false`:
      ```json
      {
        "individual_outlines": {
          "document1.pdf": "1. Introduction\n    1.1. Background\n2. Main Points\n    2.1. Sub-point A",
          "notes.txt": "1. Key Concepts\n2. Action Items"
        }
      }
      ```
    - If `combine` is `true`:
      ```json
      {
        "combined_outline": "1. Overview of All Documents\n    1.1. Common Themes\n2. Detailed Sections\n    2.1. From Document 1\n    2.2. From Document 2"
      }
      ```
  - `404 Not Found`: One or more specified files not found or not processed.

---

## Summarize Documents

- **Endpoint:** `POST /summarize`
- **Summary:** Summarize one or more documents.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"]
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "summaries": {
        "document1.pdf": "This is the summary for document1.pdf.",
        "notes.txt": "This is the summary for notes.txt."
      }
    }
    ```

---

## Generate FAQ

- **Endpoint:** `POST /generate_faq`
- **Summary:** Generate FAQs for one or more documents.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"]
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "faqs": [
        {
          "question": "What is the main topic of document1.pdf?",
          "answer": "The main topic is...",
          "source": "document1.pdf"
        },
        {
          "question": "What are the key takeaways from notes.txt?",
          "answer": "The key takeaways are...",
          "source": "notes.txt"
        }
      ]
    }
    ```

---

## Generate Quiz

- **Endpoint:** `POST /generate_quiz`
- **Summary:** Generate quizzes (MCQ or short questions) for one or more documents.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"],
    "question_type": "mcq",
    "count": 10
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "quiz": [
        {
          "question": "What is the capital of France?",
          "options": ["Berlin", "Madrid", "Paris", "Rome"],
          "answer": "Paris",
          "source": "document1.pdf"
        }
      ]
    }
    ```

---

## Generate Flashcards

- **Endpoint:** `POST /generate_flashcards`
- **Summary:** Generate flashcards for one or more documents.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"]
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "flashcards": [
        {
          "front": "What is the powerhouse of the cell?",
          "back": "Mitochondria",
          "source": "document1.pdf"
        }
      ]
    }
    ```

---

## Delete Files

- **Endpoint:** `POST /delete`
- **Summary:** Delete files from the knowledge base.
- **Input:**
  ```json
  {
    "filenames": ["document1.pdf", "notes.txt"]
  }
  ```
- **Output:**
  - `200 OK`:
    ```json
    {
      "message": "Successfully deleted 2 files."
    }
    ```
  - If some files could not be deleted:
    ```json
    {
      "message": "Some files could not be deleted.",
      "deleted_files": 1,
      "errors": ["File not found: notes.txt"]
    }
    ```
