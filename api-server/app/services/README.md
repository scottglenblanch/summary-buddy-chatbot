# RAG Pipeline Services

The RAG (Retrieval-Augmented Generation) pipeline orchestrates the entire workflow from PDF processing to generating context-aware answers.

## Architecture

```
PDF File
   ↓
PDFProcessor → Extract Text (pages)
   ↓
Text Splitter → Create Chunks (1000 tokens, 200 overlap)
   ↓
OpenAI Embeddings → Generate Embeddings
   ↓
pgvector (PostgreSQL) → Store & Index
   ↓
[Ready for Questions]
   ↓
User Question
   ↓
VectorDB Search → Retrieve Similar Chunks (k=4)
   ↓
LLM Service (GPT-4o-mini) → Generate Answer
   ↓
Save to Database & Return to User
```

## Services Overview

### 1. StorageService (`storage.py`)
Manages file storage using S3-compatible object storage (Amazon S3 in AWS, a MinIO container locally).

**Features:**
- S3-compatible object storage (S3 / MinIO)
- Auto-creates the bucket if it does not exist
- Stores original uploads and extracted texts under key prefixes

**Key Methods:**
```python
storage.save_upload(name, data)     # Store an original upload (PDF/TXT)
storage.list_uploads()              # List original uploads
storage.save_text_file()            # Save extracted text
storage.list_text_files()           # List extracted texts
storage.clear_text_files()          # Clear all texts
```

**Usage:**
```python
from app.services.storage import StorageService

storage = StorageService()  # S3-compatible storage (MinIO locally)
uploads = storage.list_uploads()
```

### 2. PDFProcessor (`pdf_processor.py`)
Extracts text from PDF files using pypdf.

**Features:**
- Page-by-page text extraction
- Skips empty pages
- Preserves page numbers and metadata
- Error handling per page

**Key Methods:**
```python
processor.extract_text_from_pdf(path)   # Extract all pages
```

**Output:**
```python
[
    {
        "title": "page_0001",
        "text": "Page content...",
        "page_number": 1,
        "source": "/path/to/pdf"
    },
    ...
]
```

**Usage:**
```python
from app.services.pdf_processor import PDFProcessor

processor = PDFProcessor()
documents = processor.extract_text_from_pdf("/path/to/pdf")
```

### 3. VectorDBService (`vector_db.py`)
Manages the pgvector vector store (in PostgreSQL) for semantic search.

**Features:**
- Text embedding using OpenAI's text-embedding-3-large
- Persistent storage in PostgreSQL via pgvector
- Similarity search with relevance scores
- Collection management

**Key Methods:**
```python
db.add_documents(documents)         # Add documents to database
db.search(query, k=4)               # Search for similar documents
db.clear()                          # Clear vector database
db.get_collection_info()            # Get database statistics
```

**Search Results:**
```python
[
    {
        "content": "Kaladin is...",
        "score": 0.8234,
        "metadata": {"title": "page_0001", "page_number": 1}
    },
    ...
]
```

**Usage:**
```python
from app.services.vector_db import VectorDBService

vdb = VectorDBService()
vdb.add_documents(documents)
results = vdb.search("Who is Kaladin?", k=4)
```

### 4. LLMService (`llm_service.py`)
Handles OpenAI API interactions for answer generation.

**Features:**
- GPT-4o-mini model (cost-efficient)
- Context-aware answer generation
- Source extraction from retrieved documents
- Configurable system prompts

**Key Methods:**
```python
llm.generate_answer(question, context)      # Generate answer with context
llm.extract_sources(documents)              # Extract source references
```

**Usage:**
```python
from app.services.llm_service import LLMService

llm = LLMService()
answer = llm.generate_answer(
    "Who is Kaladin?",
    "Kaladin is the protagonist who can fly..."
)
sources = llm.extract_sources(documents)
```

### 5. RAGPipeline (`rag_pipeline.py`)
Main orchestrator that coordinates all services.

**Features:**
- End-to-end PDF processing pipeline
- Question-answering with RAG
- Pipeline logging and monitoring
- Error handling and recovery

**Key Methods:**
```python
pipeline.process_upload(path, name) # Process an uploaded document and add embeddings
pipeline.ask_question(question)     # Answer a question with RAG
pipeline.get_status()               # Get pipeline status
```

**Upload Processing Workflow:**
1. Extract text (PDF via pypdf, or read the .txt file)
2. Save extracted text files to storage
3. Split into chunks (1000 tokens, 200 overlap)
4. Generate embeddings (OpenAI)
5. Append to pgvector store in PostgreSQL
6. Log execution in database

**Ask Question Workflow:**
1. Search vector database for relevant chunks (k=4)
2. Build context from top results
3. Generate answer using LLM with context
4. Extract source references
5. Save conversation to database
6. Return answer and sources

**Usage:**
```python
from app.services.rag_pipeline import get_rag_pipeline

pipeline = get_rag_pipeline()

# Process an uploaded document (PDF or TXT)
result = pipeline.process_upload(file_path, "document.pdf")
# Returns: {"status": "completed", "chunks_created": 250, ...}

# Ask question
response = pipeline.ask_question("Who is Kaladin?")
# Returns: {"answer": "...", "sources": [...], "conversation_id": "..."}

# Get status
status = pipeline.get_status()
# Returns: {"vector_db": {...}, "last_execution": {...}, ...}
```

## Configuration

Environment variables in `.env`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Text Chunking
CHUNK_SIZE=1000              # Tokens per chunk
CHUNK_OVERLAP=200            # Token overlap between chunks
RAG_K_RESULTS=4              # Number of results to retrieve

# Storage (S3-compatible; MinIO locally)
AWS_S3_BUCKET=summary-buddy-uploads
AWS_S3_ENDPOINT_URL=http://minio:9000

# Vector DB (PostgreSQL + pgvector; defaults to DATABASE_URL)
PGVECTOR_URL=postgresql://postgres:postgres@postgres:5432/summary_buddy_chatbot
PGVECTOR_COLLECTION_NAME=summary_buddy

# AWS (optional)
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

## Data Flow

### PDF Processing

```
PDF File (uploaded to resources/)
   ↓ [PDFProcessor.extract_text_from_pdf()]
   ↓ Extract text from each page
   ↓
Document[] (with page metadata)
   ↓ [RecursiveCharacterTextSplitter]
   ↓ Split into overlapping chunks
   ↓
Chunk[] (1000 tokens, 200 overlap)
   ↓ [OpenAI text-embedding-3-large]
   ↓ Generate vector embeddings
   ↓
Embedded Chunks
   ↓ [VectorDBService.add_documents()]
   ↓ Store in pgvector
   ↓
pgvector store in PostgreSQL (persistent)
   ↓ [RAGPipelineLog]
   ↓ Log execution status
```

### Question Answering

```
User Question
   ↓ [VectorDBService.search()]
   ↓ Find k=4 similar chunks
   ↓
Retrieved Chunks (with relevance scores)
   ↓ [Build Context]
   ↓ Combine chunks with separators
   ↓
Context String
   ↓ [LLMService.generate_answer()]
   ↓ Send to GPT-4o-mini with system prompt
   ↓
Generated Answer
   ↓ [Extract Sources]
   ↓ Get page references
   ↓
Answer + Sources
   ↓ [Save to Conversation Table]
   ↓
Response to User
```

## Performance Tuning

### Chunk Size & Overlap
- **Larger chunks** (1500+): More context, more expensive embeddings
- **Smaller chunks** (500-): More granular, easier to search
- **Overlap** (200): Prevents losing context at chunk boundaries

### Search Results (k)
- **k=4**: Balanced (current default)
- **k=1-3**: Faster, less context
- **k=5-10**: More context, slower

### Embeddings
- Uses OpenAI's `text-embedding-3-large` (most accurate)
- Costs ~$0.02 per 1M tokens

### LLM Model
- Uses `gpt-4o-mini` (cost-efficient)
- ~10x cheaper than gpt-4
- Sufficient for RAG QA task

## Monitoring & Logging

### Pipeline Logging
All pipeline executions logged to `rag_pipeline_logs` table:

```sql
SELECT * FROM rag_pipeline_logs 
ORDER BY started_at DESC 
LIMIT 10;
```

### Conversation History
All Q&A stored in `conversations` table:

```sql
SELECT * FROM conversations 
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

### Service Checks

```python
from app.services.rag_pipeline import get_rag_pipeline

pipeline = get_rag_pipeline()
status = pipeline.get_status()

print(status["vector_db"])        # Vector DB info
print(status["last_execution"])   # Last pipeline run
print(status["conversation_count"]) # Total conversations
```

## Error Handling

### PDF Processing Errors
- Missing PDF: Searches for any `.pdf` in resources
- Extraction fails: Skips problematic pages and continues
- Chunking fails: Returns raw pages as documents

### Vector DB Errors
- Connection fails: Falls back to in-memory search
- Embedding fails: Retries with exponential backoff
- Clear fails: Logs warning and continues

### LLM Errors
- API fails: Returns error message with conversation ID
- Rate limit: Queues request (not yet implemented)
- Token limit: Truncates context to fit

## Testing

### Unit Tests
```python
def test_pdf_extraction():
    processor = PDFProcessor()
    docs = processor.extract_text_from_pdf("test.pdf")
    assert len(docs) > 0

def test_vector_db_search():
    vdb = VectorDBService()
    results = vdb.search("query", k=4)
    assert len(results) <= 4

def test_rag_pipeline():
    pipeline = RAGPipeline()
    response = pipeline.ask_question("Who is Kaladin?")
    assert "answer" in response
```

### Integration Tests
```bash
# From project root
docker-compose -f docker-compose.dev.yml exec backend pytest app/services/

# With coverage
docker-compose -f docker-compose.dev.yml exec backend \
  pytest app/services/ --cov=app/services/
```

## Troubleshooting

### Vector DB Not Found
```
Error: Vector database not initialized
```
**Solution:** Run RAG pipeline to process PDF first

### PDF Not Found
```
Error: No PDF found in resources/
```
**Solution:** Place a PDF in the `resources/` directory (any `.pdf` filename works)

### OpenAI API Error
```
Error: Invalid API key
```
**Solution:** Update `OPENAI_API_KEY` in `.env`

### Embeddings Too Expensive
```
Warning: High token usage
```
**Solution:** Reduce chunk size or use cheaper embeddings model

## Future Enhancements

- [ ] Streaming responses for real-time answers
- [ ] Multi-document support (multiple PDFs)
- [ ] User-specific conversations
- [ ] Answer caching to reduce API costs
- [ ] Semantic caching with sentence transformers
- [ ] Fine-tuned embeddings for your document domain
- [ ] Conversation context window (remember previous Q&A)
- [ ] Confidence scoring for answers
- [ ] A/B testing different prompts
- [ ] Analytics dashboard

## References

- [LangChain Documentation](https://python.langchain.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [pypdf Documentation](https://pypdf.readthedocs.io/)
- [RAG Best Practices](https://github.com/langchain-ai/langchain/blob/master/docs/docs/use_cases/question_answering.md)
