import axios, { AxiosInstance } from 'axios'
import { ChatResponse, RAGPipelineResponse, MultiUploadResponse, UploadsListResponse } from '@types/index'

// Re-export shared types so components can import them from the api module
export type { ChatResponse, RAGPipelineResponse, MultiUploadResponse, UploadsListResponse } from '@types/index'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Ask the Game Master a question via RAG
 * @param question - The question to ask
 * @returns Promise containing answer and sources
 */
export async function askGameMaster(question: string): Promise<ChatResponse> {
  try {
    const response = await api.post<ChatResponse>('/ask-game-master-chatbot', {
      question,
    })
    return response.data
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : 'Failed to ask Game Master'
    )
  }
}

/**
 * Upload one or more documents (.pdf or .txt) to ingest into the knowledge base.
 * The backend converts each to text file(s), stores them, updates the vector
 * database, and runs the RAG embedding step.
 * @param files - The PDF or TXT files to upload
 * @returns Promise containing the aggregate processing result
 */
export async function uploadDocuments(files: File[]): Promise<MultiUploadResponse> {
  try {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    const response = await api.post<MultiUploadResponse>(
      '/admin/upload-document',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return response.data
  } catch (error) {
    const backendMessage =
      axios.isAxiosError(error) &&
      (error.response?.data?.message || error.response?.data?.error)
    throw new Error(
      backendMessage ||
        (error instanceof Error ? error.message : 'Failed to upload documents')
    )
  }
}

/**
 * Run the RAG pipeline to process PDF and create vector database
 * @returns Promise containing RAG pipeline status
 */
export async function runRAGPipeline(): Promise<RAGPipelineResponse> {
  try {
    const response = await api.post<RAGPipelineResponse>(
      '/admin/run-rag-pipeline'
    )
    return response.data
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : 'Failed to run RAG pipeline'
    )
  }
}

/**
 * Get the current status of the RAG pipeline
 * @returns Promise containing pipeline status
 */
export async function getPipelineStatus(): Promise<any> {
  try {
    const response = await api.get('/admin/pipeline-status')
    return response.data
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : 'Failed to get pipeline status'
    )
  }
}

/**
 * List the original uploaded documents currently stored in the knowledge base.
 * @returns Promise containing the list of stored upload filenames
 */
export async function listUploads(): Promise<UploadsListResponse> {
  try {
    const response = await api.get<UploadsListResponse>('/admin/uploads')
    return response.data
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : 'Failed to list uploaded documents'
    )
  }
}

/**
 * Download a previously uploaded document by filename.
 * @param filename - The name of the stored upload to download
 * @returns Promise that triggers the browser download
 */
export async function downloadUpload(filename: string): Promise<void> {
  try {
    const response = await api.get('/admin/download-pdf', {
      params: { filename },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : `Failed to download ${filename}`
    )
  }
}

/**
 * Download a stored PDF document
 * @returns Promise that triggers download
 */
export async function downloadPDF(): Promise<void> {
  try {
    const response = await api.get('/admin/download-pdf', {
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'document.pdf')
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? error.message
        : 'Failed to download PDF'
    )
  }
}

export default api
