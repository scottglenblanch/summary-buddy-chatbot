# Database Schema & Migrations

## Overview

The Summary Buddy Chatbot uses **PostgreSQL** as its primary database with **SQLAlchemy** as the ORM and **Alembic** for schema migrations.

## Database Schema

### Tables

#### `conversations`
Stores all conversation history between users and the Game Master.

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources JSON,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX ix_conversations_created_at ON conversations(created_at);
```

**Columns:**
- `id`: Unique identifier (UUID v4)
- `question`: User's question
- `answer`: Game Master's response
- `sources`: JSON array of source references from the PDF
- `created_at`: Timestamp when conversation was created
- `updated_at`: Timestamp when conversation was last updated

#### `rag_pipeline_logs`
Tracks RAG pipeline execution history for monitoring and debugging.

```sql
CREATE TABLE rag_pipeline_logs (
    id UUID PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    chunks_created INTEGER,
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP
);

CREATE INDEX ix_rag_pipeline_logs_status ON rag_pipeline_logs(status);
CREATE INDEX ix_rag_pipeline_logs_started_at ON rag_pipeline_logs(started_at);
```

**Columns:**
- `id`: Unique identifier (UUID v4)
- `status`: Execution status ('running', 'completed', 'failed')
- `chunks_created`: Number of text chunks created during RAG processing
- `error_message`: Error details if execution failed
- `started_at`: Timestamp when RAG pipeline started
- `completed_at`: Timestamp when RAG pipeline completed

## Models

Models are defined in `app/models/database.py` using SQLAlchemy:

```python
class Conversation(db.Model):
    id = UUID primary key
    question = Text
    answer = Text
    sources = JSON
    created_at = DateTime
    updated_at = DateTime

class RAGPipelineLog(db.Model):
    id = UUID primary key
    status = String(50)
    chunks_created = Integer
    error_message = Text
    started_at = DateTime
    completed_at = DateTime
```

## Migrations

Migrations are managed with **Alembic**, located in `app/db/migrations/`.

### Migration Files
- `env.py` - Alembic environment configuration
- `script.py.mako` - Migration template
- `versions/` - Individual migration files

### Initial Migration
**`001_initial.py`** - Creates `conversations` and `rag_pipeline_logs` tables with indexes.

## Setup & Management

### 1. Initialize Database (Local Development)

**Using Docker Compose:**
```bash
docker-compose -f docker-compose.dev.yml up -d postgres
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py init
```

**Manually:**
```bash
python app/db/manage.py init
```

### 2. Run Migrations

**Using Flask CLI:**
```bash
flask --app app.main db upgrade  # Apply all migrations
flask --app app.main db downgrade  # Revert last migration
```

**Using Alembic directly:**
```bash
cd backend
alembic upgrade head      # Apply all migrations
alembic downgrade -1      # Revert last migration
alembic current           # Show current revision
```

### 3. Seed Database

Add sample data for testing:

```bash
# Using manage.py
python app/db/manage.py seed

# Using Flask CLI
flask --app app.main db seed
```

### 4. Drop & Recreate (Development Only)

```bash
# WARNING: This deletes all data
python app/db/manage.py drop
python app/db/manage.py init
python app/db/manage.py seed
```

## CLI Commands

### Database Management

```bash
# Initialize fresh database
flask --app app.main db init

# Drop all tables (requires confirmation)
flask --app app.main db drop

# Seed with sample data
flask --app app.main db seed
```

## Creating New Migrations

### Automatic Migration (Recommended)

```bash
cd backend

# 1. Modify models in app/models/database.py

# 2. Create migration automatically
alembic revision --autogenerate -m "Add new column to conversations"

# 3. Review generated file in app/db/versions/

# 4. Apply migration
alembic upgrade head
```

### Manual Migration

```bash
cd backend

# 1. Create empty migration
alembic revision -m "Descriptive migration name"

# 2. Edit the generated file in app/db/versions/

# 3. Apply migration
alembic upgrade head
```

## Docker Workflows

### Development

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py init

# View logs
docker-compose -f docker-compose.dev.yml logs backend
```

### Production

```bash
# Start services
docker-compose up -d

# Apply migrations (should happen automatically on startup)
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current
```

## Best Practices

### Migration Guidelines

1. **Create descriptive migration names**
   ```bash
   alembic revision --autogenerate -m "Add conversation_type column"
   ```

2. **Always test migrations**
   ```bash
   # Apply migration
   alembic upgrade head
   
   # Test your changes
   
   # Downgrade to verify rollback works
   alembic downgrade -1
   
   # Reapply
   alembic upgrade head
   ```

3. **Keep migrations small and focused**
   - One migration = one logical change
   - Easier to debug and rollback if issues occur

4. **Never commit partial migrations**
   - Ensure `upgrade()` and `downgrade()` are complete
   - Test both directions

5. **Use descriptive column names and constraints**
   ```python
   op.add_column('conversations', 
       sa.Column('language', sa.String(10), 
                 nullable=False, 
                 server_default='en'))
   ```

## Troubleshooting

### Database Connection Failed

**Error:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps

# Check DATABASE_URL
docker-compose -f docker-compose.dev.yml exec backend env | grep DATABASE_URL

# Verify connection
docker-compose -f docker-compose.dev.yml exec backend psql $DATABASE_URL -c "SELECT version();"
```

### Migration Conflicts

**Error:** `alembic.util.exc.CommandError: Target database is not up to date.`

**Solution:**
```bash
# Check current status
alembic current

# Review migration history
alembic history

# If stuck, manually check version table
psql -c "SELECT * FROM alembic_version;"
```

### Models Not Reflected in Database

**Solution:**
```bash
# Check if migrations were applied
alembic current

# If migrations show as applied but table missing:
alembic downgrade base
alembic upgrade head
```

### Recreating Database from Scratch

```bash
# Drop and recreate PostgreSQL volume
docker-compose -f docker-compose.dev.yml down -v

# Start fresh
docker-compose -f docker-compose.dev.yml up -d

# Initialize and seed
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py init
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py seed
```

## Performance Considerations

### Indexes

Current indexes:
- `conversations(created_at)` - For chronological queries
- `rag_pipeline_logs(status)` - For filtering by pipeline status
- `rag_pipeline_logs(started_at)` - For historical queries

### Future Optimizations

For high-traffic scenarios, consider:
- Partitioning `conversations` table by date
- Adding indexes on `question` (full-text search)
- Archiving old conversations to a separate table

## Database Backup

### Local Development

```bash
# Backup database
docker-compose -f docker-compose.dev.yml exec postgres pg_dump -U postgres summary_buddy_chatbot > backup.sql

# Restore database
docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres summary_buddy_chatbot < backup.sql
```

### Production (AWS RDS)

```bash
# Using AWS CLI
aws rds create-db-snapshot \
  --db-instance-identifier summary-buddy-db \
  --db-snapshot-identifier summary-buddy-backup-$(date +%Y%m%d)

# Download backup
aws rds describe-db-snapshots \
  --db-snapshot-identifier summary-buddy-backup-20250101
```

## References

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
