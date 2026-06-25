export interface ChatResponse {
  answer: string
  sources?: string[]
  conversation_id: string | null
}

export interface RAGPipelineResponse {
  status: 'completed' | 'failed' | 'running'
  chunks_created?: number
  pages_processed?: number
  filename?: string
  file_type?: string
  text_files_created?: number
  message?: string
  error?: string
}

export interface MultiUploadResponse {
  status: 'completed' | 'failed' | 'partial'
  files_total: number
  files_succeeded: number
  files_failed: number
  chunks_created?: number
  text_files_created?: number
  results: RAGPipelineResponse[]
  message?: string
  error?: string
}

export interface UploadsListResponse {
  files: string[]
  count: number
}
