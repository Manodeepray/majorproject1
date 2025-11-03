import type {
  HealthResponse,
  FileStatusResponse,
  UploadResponse,
  QueryRequest,
  QueryResponse,
  DeepQueryRequest,
  DeepQueryResponse,
  SummarizeRequest,
  SummarizeResponse,
  GenerateRequest,
  FAQResponse,
  QuizRequest,
  QuizResponse,
  FlashcardResponse,
  OutlineRequest,
  OutlineResponse,
  DeleteRequest,
  DeleteResponse,
  ApiError,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

/**
 * Generic API request handler with error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        // If error response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }

      // Handle specific error codes
      if (response.status === 404) {
        throw new Error(`Not found: ${errorMessage}`);
      } else if (response.status === 503) {
        throw new Error(`Service unavailable: ${errorMessage}`);
      } else if (response.status === 500) {
        throw new Error(`Server error: ${errorMessage}`);
      } else {
        throw new Error(errorMessage);
      }
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
}

/**
 * Upload files to the knowledge base
 */
export async function uploadFiles(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const url = `${API_BASE_URL}/upload`;
  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const errorData: ApiError = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new Error(errorMessage);
  }

  return await response.json();
}

/**
 * Check API health status
 */
export async function checkHealth(): Promise<HealthResponse> {
  return apiRequest<HealthResponse>('/health');
}

/**
 * Get file processing status
 */
export async function getFileStatus(): Promise<FileStatusResponse> {
  return apiRequest<FileStatusResponse>('/file_status');
}

/**
 * Query the knowledge base
 */
export async function query(query: string, top_k: number = 5): Promise<QueryResponse> {
  const payload: QueryRequest = { query, top_k };
  return apiRequest<QueryResponse>('/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Deep query the knowledge base with multi-turn reasoning
 */
export async function deepQuery(
  query: string,
  top_k: number = 5,
  create_graph: boolean = false
): Promise<DeepQueryResponse> {
  const payload: DeepQueryRequest = { query, top_k, create_graph };
  return apiRequest<DeepQueryResponse>('/deepquery', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Generate outline(s) for documents
 */
export async function generateOutline(
  filenames: string[],
  combine: boolean = false
): Promise<OutlineResponse> {
  const payload: OutlineRequest = { filenames, combine };
  return apiRequest<OutlineResponse>('/generate_outline', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Summarize documents
 */
export async function summarize(filenames: string[]): Promise<SummarizeResponse> {
  const payload: SummarizeRequest = { filenames };
  return apiRequest<SummarizeResponse>('/summarize', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Generate FAQ for documents
 */
export async function generateFAQ(filenames: string[]): Promise<FAQResponse> {
  const payload: GenerateRequest = { filenames };
  return apiRequest<FAQResponse>('/generate_faq', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Generate quiz for documents
 */
export async function generateQuiz(
  filenames: string[],
  question_type: 'mcq' | 'short' = 'mcq',
  count: number = 10
): Promise<QuizResponse> {
  const payload: QuizRequest = { filenames, question_type, count };
  return apiRequest<QuizResponse>('/generate_quiz', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Generate flashcards for documents
 */
export async function generateFlashcards(filenames: string[]): Promise<FlashcardResponse> {
  const payload: GenerateRequest = { filenames };
  return apiRequest<FlashcardResponse>('/generate_flashcards', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Delete files from the knowledge base
 */
export async function deleteFiles(filenames: string[]): Promise<DeleteResponse> {
  const payload: DeleteRequest = { filenames };
  return apiRequest<DeleteResponse>('/delete', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

