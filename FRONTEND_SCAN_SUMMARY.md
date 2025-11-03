# Frontend Scan Summary

## Project Overview
This is a **Knowledge Base API** system that ingests documents, creates vector embeddings, and provides querying and generative AI features. It requires a Next.js frontend that interfaces with all endpoints.

## Architecture
- **Main API Server**: FastAPI on port `5000` (http://0.0.0.0:5000 or http://localhost:5000)
- **Inference Server**: FastAPI on port `8000` (internal, not directly accessed by frontend)
- **Framework**: FastAPI with uvicorn

## API Endpoints to Integrate

### 1. Health Check
- **GET** `/health`
- **Response**: `{ "status": "healthy" }`
- **Usage**: Check if backend is running

### 2. File Status
- **GET** `/file_status`
- **Response**: JSON object with file processing statuses
- **Example Response**:
```json
{
  "document1.pdf": {
    "status": "processed",
    "timestamp": "2023-10-27T10:00:00Z"
  },
  "notes.txt": {
    "status": "pending",
    "timestamp": "2023-10-27T10:05:00Z"
  }
}
```
- **Usage**: Display dashboard of uploaded files and their processing status

### 3. Upload Files
- **POST** `/upload`
- **Content-Type**: `multipart/form-data`
- **Body**: `files` (multiple files allowed: PDF, TXT, DOCX)
- **Response**:
```json
{
  "message": "Files ['document1.pdf'] uploaded successfully. Processing started in the background.",
  "detail": "The data ingestion and indexing pipeline is running..."
}
```
- **Usage**: File upload interface with drag-and-drop

### 4. Query Knowledge Base
- **POST** `/query`
- **Body**:
```json
{
  "query": "What is the impact of climate change?",
  "top_k": 5
}
```
- **Response**:
```json
{
  "answer": "The main findings indicate...",
  "context": ["Relevant chunk 1 text...", "Relevant chunk 2 text..."]
}
```
- **Usage**: Simple Q&A interface

### 5. Deep Query Knowledge Base
- **POST** `/deepquery`
- **Body**:
```json
{
  "query": "What is the impact of climate change and proposed solutions?",
  "top_k": 5,
  "create_graph": true
}
```
- **Response**:
```json
{
  "answer": "Comprehensive answer...",
  "context": ["Summarized chunk 1...", "Summarized chunk 2..."],
  "sub_queries": ["Impact of climate change", "Proposed solutions"],
  "graph_location": "/path/to/generated_knowledge_graph.html"
}
```
- **Usage**: Advanced query with multi-turn reasoning and optional knowledge graph visualization

### 6. Generate Outline
- **POST** `/generate_outline`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"],
  "combine": false
}
```
- **Response** (individual):
```json
{
  "individual_outlines": {
    "document1.pdf": "1. Introduction\n    1.1. Background\n2. Main Points"
  }
}
```
- **Response** (combined):
```json
{
  "combined_outline": "1. Overview of All Documents\n    1.1. Common Themes"
}
```
- **Usage**: Document outline generation interface

### 7. Summarize Documents
- **POST** `/summarize`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"]
}
```
- **Response**:
```json
{
  "summaries": [
    {
      "filename": "document1.pdf",
      "summary": "This is the summary..."
    }
  ]
}
```
- **Usage**: Document summarization interface

### 8. Generate FAQ
- **POST** `/generate_faq`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"]
}
```
- **Response**:
```json
{
  "faqs": [
    {
      "question": "What is the main topic?",
      "answer": "The main topic is...",
      "source": "document1.pdf"
    }
  ]
}
```
- **Usage**: FAQ generation and display interface

### 9. Generate Quiz
- **POST** `/generate_quiz`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"],
  "question_type": "mcq",
  "count": 10
}
```
- **Response**:
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
- **Usage**: Interactive quiz interface (MCQ or short answer)

### 10. Generate Flashcards
- **POST** `/generate_flashcards`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"]
}
```
- **Response**:
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
- **Usage**: Flashcard study interface with flip functionality

### 11. Delete Files
- **POST** `/delete`
- **Body**:
```json
{
  "filenames": ["document1.pdf", "notes.txt"]
}
```
- **Response**:
```json
{
  "message": "Successfully deleted 2 files."
}
```
- **Usage**: File management with delete confirmation

## Frontend Requirements

### Core Pages/Components Needed:
1. **Dashboard/Home Page**
   - File status display (with refresh)
   - Upload interface (drag & drop)
   - Quick stats

2. **Query Page**
   - Simple query interface
   - Deep query interface (with graph toggle)
   - Response display (answer + context)
   - Sub-queries display (for deep query)
   - Knowledge graph viewer (if available)

3. **Document Management**
   - File upload
   - File status list
   - Delete functionality

4. **Generative Features**
   - **Outline Generator**: File selector, combine toggle, outline display
   - **Summarizer**: File selector, summary display
   - **FAQ Generator**: File selector, FAQ accordion/cards
   - **Quiz Generator**: File selector, question type (MCQ/short), count, interactive quiz
   - **Flashcard Generator**: File selector, flip-card interface

### UI/UX Considerations:
- Loading states for all async operations
- Error handling and display
- Success notifications
- Responsive design
- Modern, clean interface
- File status indicators (processed/pending/error)

### Technical Stack for Next.js:
- **Framework**: Next.js 14+ (App Router recommended)
- **Styling**: Tailwind CSS (recommended for modern UI)
- **State Management**: React hooks + Context API or Zustand
- **HTTP Client**: fetch API or axios
- **File Upload**: Native FormData or react-dropzone
- **Graph Visualization**: Iframe for HTML knowledge graphs or D3.js/vis.js integration

### Environment Variables Needed:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

### Knowledge Graph Handling:
- Knowledge graphs are returned as HTML file paths
- Need to serve these HTML files or integrate them into React
- Consider iframe embedding or parsing HTML for visualization

## Important Notes:
1. **Processing Time**: File uploads trigger background processing - users need to wait and check file_status
2. **Vector Store**: Queries require processed files - check file_status before allowing queries
3. **Long Requests**: Some endpoints (deepquery, quiz generation) may take time - implement proper loading states
4. **CORS**: Ensure backend has CORS configured for Next.js origin
5. **File Types**: Supports PDF, TXT, DOCX
6. **Error Handling**: 404 (no results), 503 (vector store unavailable), 500 (server errors)

## Recommended Project Structure:
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (Dashboard)
│   ├── query/
│   │   └── page.tsx
│   ├── generate/
│   │   ├── outline/
│   │   ├── summarize/
│   │   ├── faq/
│   │   ├── quiz/
│   │   └── flashcards/
│   └── api/ (if needed for proxy)
├── components/
│   ├── FileUpload.tsx
│   ├── FileStatus.tsx
│   ├── QueryInterface.tsx
│   ├── DeepQueryInterface.tsx
│   ├── OutlineViewer.tsx
│   ├── FAQViewer.tsx
│   ├── QuizViewer.tsx
│   └── FlashcardViewer.tsx
├── lib/
│   └── api.ts (API client functions)
├── types/
│   └── api.ts (TypeScript types)
└── public/ (for static assets)
```

