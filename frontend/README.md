# Knowledge Base Frontend

A modern Next.js frontend application for the Knowledge Base API. This application provides a comprehensive interface for uploading documents, querying your knowledge base, and generating content using AI.

## Features

- **Document Management**: Upload and manage documents (PDF, TXT, DOCX)
- **File Status Tracking**: Monitor file processing status in real-time
- **Query Interface**: Simple and deep query capabilities with knowledge graph visualization
- **Content Generation**:
  - Document outlines
  - Summaries
  - FAQs
  - Interactive quizzes (MCQ and short answer)
  - Flashcards with flip animation

## Prerequisites

- Node.js 18+ and npm
- Backend API server running (see main project README)

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   Create a `.env.local` file in the frontend directory:
   ```env
   NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
   ```
   Replace with your backend API URL.

3. **Run development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── query/             # Query pages
│   └── generate/          # Content generation pages
├── components/            # Reusable React components
├── lib/                   # API client and utilities
├── types/                 # TypeScript type definitions
└── public/                # Static assets
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL | `http://localhost:5000` |

## Deployment to Vercel

1. **Push your code to GitHub**

2. **Import project to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your repository
   - Select the `frontend` directory as the root directory

3. **Configure environment variables**:
   - In Vercel project settings, add `NEXT_PUBLIC_API_BASE_URL` with your production API URL

4. **Deploy**:
   - Vercel will automatically deploy on push to main branch
   - Or manually deploy from the dashboard

### Vercel Configuration Notes

- The `vercel.json` file is already configured for Next.js
- Ensure your backend API allows CORS from your Vercel domain
- Update `NEXT_PUBLIC_API_BASE_URL` with your production backend URL

## API Integration

The frontend integrates with the following backend endpoints:

- `GET /health` - Health check
- `GET /file_status` - Get file processing status
- `POST /upload` - Upload documents
- `POST /query` - Simple query
- `POST /deepquery` - Deep query with knowledge graph
- `POST /generate_outline` - Generate document outlines
- `POST /summarize` - Generate summaries
- `POST /generate_faq` - Generate FAQs
- `POST /generate_quiz` - Generate quizzes
- `POST /generate_flashcards` - Generate flashcards
- `POST /delete` - Delete files

See `endpoints.md` in the main project directory for detailed API documentation.

## Technologies

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **React** - UI library

## Troubleshooting

### CORS Errors

If you encounter CORS errors:
1. Ensure the backend has CORS middleware configured (see `src/server.py`)
2. Check that `NEXT_PUBLIC_API_BASE_URL` matches your backend URL

### Build Errors

- Ensure all environment variables are set
- Check that the backend API is accessible from your deployment environment

### File Upload Issues

- Verify file types are supported (PDF, TXT, DOCX)
- Check file size limits (50MB per file)
- Ensure backend is running and accessible

## Contributing

This frontend is part of the Knowledge Base project. See the main project README for contribution guidelines.
