# Local Development Setup Scripts

This directory contains setup scripts to quickly initialize the local development environment.

## Quick Start

### Windows (PowerShell)

```powershell
# Make the script executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup.ps1
```

### Linux / macOS / WSL

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### Cross-Platform (Python)

```bash
# Run with Python
python setup.py

# Or with Python 3 explicitly
python3 setup.py
```

## What the Setup Script Does

1. **Checks Prerequisites**
   - Verifies Docker is installed
   - Verifies Docker Compose is installed
   - Warns about optional tools (Node.js, Python)

2. **Environment Configuration**
   - Copies `.env.example` to `.env` (if not already present)
   - Reminds you to update with your actual configuration

3. **Docker Setup**
   - Stops any existing containers
   - Starts fresh Docker containers:
     - PostgreSQL database
     - Flask backend
     - React frontend
   - Waits for services to become healthy

4. **Database Setup**
   - Initializes database schema
   - Creates tables (Conversation, RAGPipelineLog)
   - Seeds with sample data

5. **Displays Startup Information**
   - Shows service URLs
   - Provides next steps
   - Lists useful commands
   - Links to documentation

## Prerequisites

### Required
- **Docker** - For containerized services
  - [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Or via package manager:
    ```bash
    # macOS
    brew install docker

    # Ubuntu/Debian
    sudo apt-get install docker.io docker-compose

    # Windows
    choco install docker-desktop
    ```

### Optional (for local development without Docker)
- **Node.js** - For local frontend development
- **Python 3.11+** - For local backend development

## What Gets Started

After running the setup script, the following services are available:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React UI (Game Master chat, Admin panel) |
| Backend API | http://localhost:5000/api | Flask REST API |
| Database | localhost:5432 | PostgreSQL database |

## Environment Configuration

The script creates a `.env` file from `.env.example`. You need to update it with:

### Required
- `OPENAI_API_KEY` - Your OpenAI API key

### Optional
- `DB_PASSWORD` - Database password (default: postgres)
- `AWS_S3_BUCKET` - S3 bucket for production
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

## Common Issues

### "Docker daemon is not running"
```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker

# Windows
# Start Docker Desktop application
```

### Port Already in Use
If port 3000, 5000, or 5432 is already in use, modify `docker-compose.dev.yml`:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change to 3001
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps

# Check logs
docker-compose -f docker-compose.dev.yml logs postgres

# Restart the service
docker-compose -f docker-compose.dev.yml restart postgres
```

### Setup Script Fails
```bash
# Try manual setup
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py init
docker-compose -f docker-compose.dev.yml exec backend python app/db/manage.py seed
```

## Useful Commands After Setup

```bash
# View logs from all services
docker-compose -f docker-compose.dev.yml logs -f

# View backend logs only
docker-compose -f docker-compose.dev.yml logs -f backend

# Access backend shell
docker-compose -f docker-compose.dev.yml exec backend bash

# Run backend tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Stop all services
docker-compose -f docker-compose.dev.yml down

# Reset database (delete all data)
docker-compose -f docker-compose.dev.yml down -v

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend
```

## Development Workflow

1. **Make code changes** - Edit source files directly
2. **Hot reload** - Changes are reflected automatically:
   - Frontend: Vite hot module replacement
   - Backend: Python auto-restart on code changes
3. **View changes** - Refresh browser or check logs
4. **Test** - Use `/admin` page to test RAG pipeline
5. **Stop** - `docker-compose -f docker-compose.dev.yml down` when done

## Next Steps

1. **Update .env** with your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

2. **Open the application**:
   - Frontend: http://localhost:3000
   - Admin panel: http://localhost:3000/admin

3. **Test the chatbot**:
   - Ask a question in the chat interface
   - Watch real-time responses from the Game Master

4. **Manage RAG pipeline**:
   - Visit the admin panel
   - Download the uploaded PDF
   - Click "Run RAG Pipeline" to process the PDF

## Troubleshooting Scripts

### Python Script Issues
```bash
# Ensure Python 3 is available
python3 --version

# Run with verbose output
python3 setup.py --verbose
```

### Bash Script Issues (Linux/Mac)
```bash
# Check script is executable
ls -l setup.sh

# Run with bash explicitly
bash setup.sh

# Run with debug output
bash -x setup.sh
```

### PowerShell Script Issues (Windows)
```powershell
# Check execution policy
Get-ExecutionPolicy

# Set to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run with verbose output
Set-PSDebug -Trace 1; .\setup.ps1
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project Documentation](../ARCHITECTURE.md)
- [Backend Setup](../api-server/README.md)
- [Frontend Setup](../webui/README.md)

## Need Help?

- Check [DOCKER.md](../DOCKER.md) for Docker-specific issues
- Review [ARCHITECTURE.md](../ARCHITECTURE.md) for system overview
- Check service logs: `docker-compose -f docker-compose.dev.yml logs -f`
- Verify prerequisites are installed and working
