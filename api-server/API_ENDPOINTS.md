# API Endpoints Documentation

Complete reference for all backend API endpoints.

## Base URL

```
http://localhost:5000/api
```

## Health Check

### GET /health

Check if the backend service is running.

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

## Chatbot Endpoints

### POST /ask-ai-summary-buddy

Ask the Game Master a question about your uploaded documents. Uses RAG (Retrieval-Augmented Generation) to provide context-aware answers.

**Request:**
```json
{
  "question": "Who is Kaladin?"
}
```

**Response (200 OK):**
```json
{
  "answer": "Kaladin is a character described in the uploaded documents.",
  "sources": [
    "page_0045 (page 45)",
    "page_0089 (page 89)"
  ],
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid request",
  "details": [...]
}
```

**Response (400 Bad Request - No context found):**
```json
{
  "answer": "I couldn't find relevant information about that topic in the knowledge base.",
  "sources": [],
  "error": "No relevant documents found"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error",
  "message": "Error details here"
}
```

**Notes:**
- Question must be a non-empty string
- Requires documents to be uploaded and processed first (POST /admin/upload-documents)
- Returns top 4 most relevant sources from the knowledge base
- Conversations are automatically saved to the database

---

## Admin Endpoints

All admin endpoints are prefixed with `/admin`.

### GET /admin/pipeline-status

Get the current status of the RAG pipeline, including vector database statistics and last execution details.

**Response (200 OK):**
```json
{
  "vector_db": {
    "status": "initialized",
    "document_count": 250,
    "collection_name": "summary_buddy",
    "backend": "postgresql+pgvector"
  },
  "last_execution": {
    "status": "completed",
    "chunks_created": 250,
    "started_at": "2024-06-24T12:30:45.123456",
    "completed_at": "2024-06-24T12:31:15.654321"
  },
  "conversation_count": 42,
  "status": "ready"
}
```

**Response (500 Internal Server Error):**
```json
{
  "status": "error",
  "error": "Failed to get pipeline status",
  "message": "Error details here"
}
```

**Notes:**
- Vector DB status shows "not initialized" if pipeline hasn't been run yet
- last_execution is null if pipeline has never been run
- conversation_count includes all Q&A interactions

---

### GET /admin/download-pdf

Download a stored PDF document.

**Response (200 OK):**
- File stream with Content-Type: application/pdf
- File name: document.pdf

**Response (404 Not Found):**
```json
{
  "error": "PDF not found in resources directory"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "Failed to download PDF",
  "message": "Error details here"
}
```

**Notes:**
- Requires PDF to be placed in `resources/` directory
- Uses storage service which supports both local files and S3

---

## Data Models

### AskQuestionRequest

```json
{
  "question": "string (required, non-empty)"
}
```

### ChatResponse

```json
{
  "answer": "string",
  "sources": ["string"],
  "conversation_id": "uuid"
}
```

### RAGPipelineResponse

```json
{
  "status": "completed|failed",
  "chunks_created": "number",
  "pages_processed": "number (optional)",
  "message": "string",
  "error": "string (optional)"
}
```

### PipelineStatus

```json
{
  "vector_db": {
    "status": "initialized|not initialized|error",
    "document_count": "number",
    "collection_name": "string",
    "backend": "postgresql+pgvector"
  },
  "last_execution": {
    "status": "completed|failed",
    "chunks_created": "number",
    "started_at": "ISO 8601 datetime",
    "completed_at": "ISO 8601 datetime"
  },
  "conversation_count": "number",
  "status": "ready|error"
}
```

---

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request data or operation failed
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side error

### Error Response Format

```json
{
  "error": "Error title",
  "message": "Detailed error message"
}
```

### Common Error Scenarios

| Scenario | Status | Response |
|----------|--------|----------|
| Missing question field | 400 | `{"error": "Invalid request", "details": [...]}` |
| RAG pipeline not initialized | 400 | `{"answer": "I couldn't find relevant information...", "error": "No relevant documents found"}` |
| OpenAI API error | 500 | `{"error": "Internal server error", "message": "..."}` |
| Database error | 500 | `{"error": "Internal server error", "message": "..."}` |

---

## Usage Examples

### Example 1: Basic Question

```bash
curl -X POST http://localhost:5000/api/ask-ai-summary-buddy \
  -H "Content-Type: application/json" \
  -d '{"question": "Who is Kaladin?"}'
```

### Example 2: Check Pipeline Status

```bash
curl http://localhost:5000/api/admin/pipeline-status
```

### Example 3: Python Client

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Ask a question
response = requests.post(
    f"{BASE_URL}/ask-ai-summary-buddy",
    json={"question": "Tell me about the Knights Radiant"}
)
print(response.json())

# Get status
response = requests.get(f"{BASE_URL}/admin/pipeline-status")
print(response.json())
```

### Example 4: TypeScript/JavaScript Client

```typescript
const BASE_URL = "http://localhost:5000/api";

async function askQuestion(question: string) {
  const response = await fetch(`${BASE_URL}/ask-ai-summary-buddy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question })
  });
  return response.json();
}

async function getPipelineStatus() {
  const response = await fetch(`${BASE_URL}/admin/pipeline-status`);
  return response.json();
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production:
- Per IP address
- Per user (when authentication is added)
- Per endpoint

---

## Authentication

Currently, no authentication is required for any endpoints. For production:
- Add API key authentication
- Implement JWT tokens
- Add role-based access control (RBAC) for admin endpoints

---

## CORS Configuration

CORS is enabled for all origins in development. Production configuration:

```python
# frontend/.env
VITE_API_BASE_URL=https://api.yourdomain.com
```

```python
# api-server/.env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Monitoring & Logging

All endpoints log requests and responses:

```bash
# View logs in Docker
docker-compose -f docker-compose.dev.yml logs -f backend

# View logs with timestamps
docker-compose -f docker-compose.dev.yml logs --timestamps -f backend
```

Log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with full stack traces

---

## Performance Metrics

### Typical Response Times

| Endpoint | Typical Time | Notes |
|----------|--------------|-------|
| GET /health | 10ms | Fast health check |
| POST /ask-ai-summary-buddy | 1-3s | Depends on network and LLM API |
| GET /admin/pipeline-status | 50ms | Fast database query |
| GET /admin/download-pdf | 100-500ms | Depends on file size |

### API Costs (with OpenAI)

| Operation | Cost | Notes |
|-----------|------|-------|
| Embedding (1M tokens) | $0.02 | Text-embedding-3-large |
| Chat completion | $0.15 (input) / $0.60 (output) | gpt-4o-mini |
| Per question | ~$0.001-0.005 | Embedding + chat completion |

---

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Request/response caching
- [ ] Streaming responses
- [ ] Conversation context window
- [ ] Analytics and metrics
- [ ] Request tracing (OpenTelemetry)
- [ ] API versioning (/v1, /v2)
- [ ] OpenAPI/Swagger documentation
- [ ] Async task queue for long operations

---

## Troubleshooting

### RAG Pipeline Not Responding

```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Check logs
docker-compose -f docker-compose.dev.yml logs backend

# Restart backend
docker-compose -f docker-compose.dev.yml restart backend
```

### Vector Database Errors

```bash
# Check database status
curl http://localhost:5000/api/admin/pipeline-status

# Inspect vector tables in PostgreSQL
docker-compose -f docker-compose.dev.yml exec postgres \
  psql -U postgres -d summary_buddy_chatbot -c "SELECT COUNT(*) FROM langchain_pg_embedding;"
```

### OpenAI API Errors

```bash
# Verify API key
docker-compose -f docker-compose.dev.yml exec backend \
  python -c "import os; print('API Key:', 'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set')"

# Check API key validity
docker-compose -f docker-compose.dev.yml exec backend \
  python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list().data[0].id)"
```

---

## References

- [API Blueprint Implementation](../app/api/)
- [RAG Pipeline Services](../app/services/)
- [Database Models](../app/models/)
- [Frontend API Client](../../frontend/src/services/api.ts)
- [Complete Backend README](../README.md)
