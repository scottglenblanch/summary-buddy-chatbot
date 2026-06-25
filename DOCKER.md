# Summary Buddy Chatbot - Docker Setup

## Quick Start

### Development

```bash
# Copy environment variables
cp .env.example .env

# Start all services (PostgreSQL, Backend, Frontend)
docker-compose -f docker-compose.dev.yml up
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **PostgreSQL**: localhost:5432

### Production

```bash
# Copy and edit environment variables
cp .env.example .env
# Edit .env with production values

# Build and start services
docker-compose up -d
```

Services will be available at:
- **Frontend**: http://localhost (Nginx reverse proxy)
- **Backend API**: http://localhost/api
- **PostgreSQL**: Internal only (no external port)

## Docker Files

### Frontend

**Dockerfile** (Production):
- Multi-stage build (Node.js builder + Nginx runtime)
- Vite builds React app
- Nginx serves static files and proxies `/api` to backend
- Health checks enabled

**Dockerfile.dev** (Development):
- Vite dev server with hot reload
- Mounts source code for live updates

**nginx.conf**:
- Reverse proxy for backend API
- React Router fallback for SPA
- Gzip compression
- Static asset caching (1 year)
- CORS headers for API calls

### Backend

**Dockerfile** (Production & Development):
- Python 3.11 slim image
- Gunicorn production server (4 workers)
- Health checks enabled
- PostgreSQL client for migrations

### Database

**PostgreSQL 15**:
- Alpine image (minimal size)
- Persistent volume: `postgres_data`
- Environment variables for credentials

## Docker Compose Files

### docker-compose.dev.yml (Development)

```yaml
Services:
├── postgres (PostgreSQL 15)
├── backend (Flask + Gunicorn on port 5000)
└── frontend (Vite dev server on port 3000)

Volumes:
├── postgres_data_dev (database)
├── ./api-server (source code - hot reload)
└── ./webui/src (source code - hot reload)

Network: summary-buddy-network (bridge)
```

**Development Workflow**:
- Edit source code → Changes reflected immediately
- Backend: Python process restarts on code changes
- Frontend: Vite hot reload for instant updates
- Database persists between restarts

**Commands**:
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend

# Run database migrations
docker-compose -f docker-compose.dev.yml exec backend flask db upgrade

# SSH into container
docker-compose -f docker-compose.dev.yml exec backend bash
docker-compose -f docker-compose.dev.yml exec frontend sh

# Stop services
docker-compose -f docker-compose.dev.yml down

# Remove volumes (reset database)
docker-compose -f docker-compose.dev.yml down -v
```

### docker-compose.yml (Production)

```yaml
Services:
├── postgres (PostgreSQL 15 - no external port)
├── backend (Flask + Gunicorn on internal port 5000)
└── frontend (Nginx on ports 80/443)

Volumes:
├── postgres_data (database)
└── ./resources (PDF and vector DB)

Network: summary-buddy-network (bridge)
```

**Production Configuration**:
- Frontend served by Nginx with reverse proxy
- No direct backend port exposure
- Database only accessible internally
- Resource limits can be added via `deploy` section
- Health checks for auto-restart

**Commands**:
```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose stop

# Remove services
docker-compose down
```

## Environment Variables

**Required for both dev and prod**:
```env
# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=summary_buddy_chatbot

# OpenAI
OPENAI_API_KEY=sk-...

# Optional: AWS S3
AWS_S3_BUCKET=your-bucket
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

## Networking

### Internal Communication
- Frontend → Backend: `http://backend:5000/api`
- Backend → PostgreSQL: `postgresql://postgres:postgres@postgres:5432/summary_buddy_chatbot`

### External Access
- **Development**: Direct port access (3000, 5000, 5432)
- **Production**: Only port 80 exposed (Nginx reverse proxy)

## Data Persistence

### Volumes
- `postgres_data`: PostgreSQL database
- `./resources`: PDF and vector database files (mounted from host)

### Development
```bash
# Keep data between restarts
docker-compose -f docker-compose.dev.yml down

# Remove data and start fresh
docker-compose -f docker-compose.dev.yml down -v
```

## Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is healthy
docker-compose -f docker-compose.dev.yml ps

# Check logs
docker-compose -f docker-compose.dev.yml logs postgres
```

### Backend Can't Connect to Database
```bash
# Verify DATABASE_URL is correct
docker-compose -f docker-compose.dev.yml exec backend env | grep DATABASE_URL

# Test connection
docker-compose -f docker-compose.dev.yml exec backend psql $DATABASE_URL
```

### Frontend Can't Connect to Backend
```bash
# Check CORS_ORIGINS includes frontend URL
docker-compose -f docker-compose.dev.yml exec backend env | grep CORS_ORIGINS

# Test backend health
curl http://localhost:5000/api/health
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml
# Example: change "5000:5000" to "5001:5000"

# Or kill process using port
lsof -i :5000
kill -9 <PID>
```

## Production Deployment

### AWS ECS/Fargate
See [Terraform Configuration](../terraform/README.md) for automated deployment.

### Manual Deployment
1. Push images to Docker registry (ECR, Docker Hub)
2. Update docker-compose.yml with registry URLs
3. Deploy on target server with Docker Compose

```bash
# Build and push images
docker build -t registry/summary-buddy-frontend:latest ./webui
docker build -t registry/summary-buddy-backend:latest ./api-server
docker push registry/summary-buddy-frontend:latest
docker push registry/summary-buddy-backend:latest

# Deploy
docker-compose -f docker-compose.yml pull
docker-compose -f docker-compose.yml up -d
```

## Health Checks

All services have health checks:
```bash
# View health status
docker-compose ps

# Manual health check
curl http://localhost:5000/api/health
curl http://localhost/
```

## Performance Tips

### Development
- Use `.dev` compose file for hot reload
- Mount only necessary directories
- Use `-d` flag to run in background

### Production
- Use multi-stage builds (already implemented)
- Pin image versions (not `latest`)
- Set resource limits in `deploy` section
- Use health checks for auto-restart
- Regular database backups

## References
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/)
