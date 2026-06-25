# Summary Buddy Chatbot - Backend

Flask-based backend for the Summary Buddy Chatbot with RAG capabilities.

## Project Structure

```
api-server/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── main.py                  # Entry point for local development
│   ├── api/
│   │   ├── chatbot.py          # POST /ask-ai-summary-buddy
│   │   ├── admin.py            # Admin endpoints
│   │   └── health.py           # GET /health
│   ├── services/
│   │   ├── rag_pipeline.py     # RAG orchestration
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   ├── vector_db.py        # pgvector operations
│   │   ├── llm_service.py      # OpenAI integration
│   │   └── storage.py          # S3/Local file handling
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas (TODO)
│   ├── db/
│   │   └── migrations/         # Alembic migrations
│   └── utils/
│       └── logger.py           # Logging utilities
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project metadata
├── .env.example                # Environment variables template
├── wsgi.py                     # WSGI entry point for Gunicorn
└── Dockerfile                  # Docker configuration (TODO)
```

## Setup

### Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database:**
   ```bash
   # First, ensure PostgreSQL is running
   # Then create database and tables
   flask db upgrade  # Once migrations are set up
   ```

5. **Run development server:**
   ```bash
   python app/main.py
   # Or with Flask CLI:
   flask --app app.main run
   ```

Server will be available at `http://localhost:5000`

### Docker Development

```bash
docker-compose up backend
```

## API Endpoints

### Chat
- **POST** `/api/ask-ai-summary-buddy`
  - Ask the Game Master a question
  - Request: `{ "question": "Your question" }`
  - Response: `{ "answer": "...", "sources": [...], "conversation_id": "..." }`

### Admin
- **GET** `/api/admin/download-pdf`
  - Download an uploaded PDF

- **POST** `/api/admin/upload-documents`
  - Upload documents, extract text, and update the vector database

### Health
- **GET** `/api/health`
  - Health check endpoint for load balancers

## Dependencies

- **Flask 3.0**: Web framework
- **SQLAlchemy 2.0**: ORM for database
- **Psycopg2**: PostgreSQL adapter
- **Alembic**: Database migrations
- **Pydantic**: Data validation
- **LangChain**: RAG orchestration
- **pgvector**: PostgreSQL vector store extension
- **OpenAI**: LLM and embeddings
- **Boto3**: AWS S3 integration
- **Gunicorn**: Production WSGI server

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `FLASK_ENV`: Environment (development, testing, production)
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key
- `AWS_S3_BUCKET`: S3 bucket name for PDF storage
- `PGVECTOR_URL`: Vector store connection string (defaults to `DATABASE_URL`)
- `PGVECTOR_COLLECTION_NAME`: pgvector collection name (default `summary_buddy`)

## Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Database migrations
flask db init        # Initialize migrations
flask db migrate     # Create migration
flask db upgrade     # Apply migrations
flask db downgrade   # Revert migration
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn --workers 4 --worker-class sync --bind 0.0.0.0:5000 wsgi:app
```

### Using Docker

```bash
docker build -t summary-buddy-backend .
docker run -p 5000:5000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="..." \
  -e FLASK_ENV=production \
  summary-buddy-backend
```

## Database Migrations

Migrations are managed with Alembic. After updating models:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## TODO

- [ ] Implement RAG pipeline service
- [ ] PDF processor service
- [ ] Vector DB service
- [ ] LLM service
- [ ] Storage service (S3/Local)
- [ ] Database migrations
- [ ] API request/response validation with Pydantic schemas
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error handling and logging

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [LangChain Documentation](https://python.langchain.com/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
