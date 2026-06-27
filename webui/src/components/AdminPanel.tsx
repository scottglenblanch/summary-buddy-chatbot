import React, { useState, useRef, useEffect, useCallback } from 'react'
import { downloadUpload, listUploads, uploadDocuments } from '@services/api'
import '../styles/AdminPanel.css'

export default function AdminPanel() {

  const [uploadLoading, setUploadLoading] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [filesLoading, setFilesLoading] = useState(false)
  const [downloadingFile, setDownloadingFile] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)


  const refreshUploadedFiles = useCallback(async () => {
    setFilesLoading(true)
    try {
      const response = await listUploads()
      setUploadedFiles(response.files)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load uploaded files')
    } finally {
      setFilesLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUploadedFiles()
  }, [refreshUploadedFiles])


  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setError('')
    setSuccess('')
    setSelectedFiles(Array.from(event.target.files ?? []))
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please choose one or more .pdf or .txt files to upload.')
      return
    }

    setError('')
    setSuccess('')
    setUploadLoading(true)

    try {
      const response = await uploadDocuments(selectedFiles)

      if (response.status === 'failed') {
        setError(`❌ Upload failed: ${response.message || response.error || 'Unknown error'}`)
      } else {
        const prefix = response.status === 'partial' ? '⚠️' : '✅'
        setSuccess(
          `${prefix} Processed ${response.files_succeeded}/${response.files_total} file(s): added ` +
            `${response.chunks_created ?? '?'} chunks and created ` +
            `${response.text_files_created ?? '?'} text file(s).`
        )
        if (response.files_failed === 0) {
          setSelectedFiles([])
          if (fileInputRef.current) fileInputRef.current.value = ''
        }
      }

      // Refresh the list of stored uploads after the RAG process runs
      await refreshUploadedFiles()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload documents')
    } finally {
      setUploadLoading(false)
    }
  }

  const handleDownload = async (filename: string) => {
    setError('')
    setDownloadingFile(filename)
    try {
      await downloadUpload(filename)
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to download ${filename}`)
    } finally {
      setDownloadingFile(null)
    }
  }

  return (
    <div className="admin-panel">
      <div className="admin-controls">
        <section className="control-section">
          <h2>📤 Upload Documents</h2>
          <p>Upload one or more <strong>.pdf</strong> or <strong>.txt</strong> files to add to the knowledge base.</p>
          <p className="help-text">
            PDFs are converted to per-page text files and large text files are
            split into smaller files. Each upload updates the vector database and
            runs the RAG embedding step automatically. Files are stored in a
            dedicated storage container (S3 in production).
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            multiple
            aria-label="Upload PDF or text documents"
            title="Upload PDF or text documents"
            onChange={handleFileChange}
            disabled={uploadLoading}
          />

          {selectedFiles.length > 0 && (
            <ul className="selected-files">
              {selectedFiles.map((file) => (
                <li key={file.name}>
                  📄 {file.name}{' '}
                  <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                </li>
              ))}
            </ul>
          )}

          <button
            onClick={handleUpload}
            disabled={uploadLoading || selectedFiles.length === 0}
            className="admin-button primary"
          >
            {uploadLoading ? '⏳ Uploading & processing...' : '📤 Upload & Process'}
          </button>
        </section>

        <section className="control-section">

          <div className="status-header">
            <h2>Uploaded Documents</h2>
            <button
              onClick={refreshUploadedFiles}
              disabled={filesLoading}
              className="refresh-button"
            >
              {filesLoading ? '🔄 Loading...' : '🔄 Refresh'}
            </button>
          </div>
          <p>Documents currently stored in the knowledge base.</p>

          {filesLoading && uploadedFiles.length === 0 && (
            <p className="loading-text">Loading uploaded files...</p>
          )}
          {!filesLoading && uploadedFiles.length === 0 && (
            <p className="text-muted">No documents have been uploaded yet.</p>
          )}
          {uploadedFiles.length > 0 && (
            <ul className="uploaded-files">
              {uploadedFiles.map((filename) => (
                <li key={filename} className="uploaded-file">
                  <span className="uploaded-file-name">📄 {filename}</span>
                  <button
                    onClick={() => handleDownload(filename)}
                    disabled={downloadingFile === filename}
                    className="admin-button secondary download-button"
                  >
                    {downloadingFile === filename ? '⬇️ Downloading...' : '⬇️ Download'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>


        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            <div className="error-content">
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {success && (
          <div className="success-message">
            <span className="success-icon">✅</span>
            <div className="success-content">{success}</div>
          </div>
        )}

  
      </div>

      <section className="info-section">
        <h3>ℹ️ How to Use</h3>
        <ol>
          <li>Choose one or more .pdf or .txt files to upload</li>
          <li>Click “Upload &amp; Process” — the RAG/vector step runs automatically</li>
          <li>Wait for completion (you'll see the status update)</li>
          <li>Go to the Chat page and start asking questions</li>
          <li>Download any uploaded document from the list anytime</li>
        </ol>
      </section>
    </div>
  )
}
