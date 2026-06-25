# Summary Buddy Chatbot - System Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Client"
        Browser["🌐 Web Browser"]
    end

    subgraph "Frontend - React/TypeScript"
        direction TB
        GameUI["Game Master Chat<br/>/game-master-chatbot"]
        AdminUI["Admin Panel<br/>/admin"]
    end

    subgraph "Nginx Reverse Proxy"
        Nginx["Nginx Server<br/>Port 80/443"]
    end

    subgraph "Backend - Flask/Python"
        direction TB
        App["Flask App"]
        ChatAPI["POST /api/ask-game-master-chatbot<br/>Handle user questions"]
        AdminAPI["GET /api/admin/download-pdf<br/>POST /api/admin/run-rag-pipeline"]
        HealthAPI["GET /api/health"]
    end

    subgraph "Backend Services"
        direction TB
        RAG["RAG Pipeline<br/>Orchestrator"]
        PDFProc["PDF Processor<br/>PDF → Text Files"]
        VectorDB["Vector DB Service<br/>pgvector Operations"]
        LLMSvc["LLM Service<br/>OpenAI Integration"]
        Storage["Storage Service<br/>S3/Local File Ops"]
    end

    subgraph "Data Layer - Local Dev"
        direction TB
        PGLocal["PostgreSQL + pgvector<br/>Conversations, Metadata<br/>& Embeddings"]
        LocalPDF["Local PDF<br/>Docker Volume"]
        LocalTexts["Text Files<br/>Docker Volume"]
    end

    subgraph "Data Layer - AWS Production"
        direction TB
        RDSDB["RDS PostgreSQL + pgvector<br/>Multi-AZ<br/>Private Subnet"]
        S3Private["S3 Bucket<br/>Private<br/>PDF + Text Files"]
    end

    subgraph "External Services"
        OpenAI["OpenAI API<br/>GPT-4 + Embeddings"]
    end

    subgraph "AWS Infrastructure - Production"
        direction TB
        ALB["Application Load Balancer<br/>Public Facing"]
        FrontendTask["ECS Task<br/>Frontend<br/>Auto-scaled"]
        BackendTask["ECS Task<br/>Backend<br/>Auto-scaled"]
        IAM["IAM Role<br/>S3 Access Policy"]
    end

    Browser -->|HTTP/HTTPS| Nginx
    Nginx -->|Routes| GameUI
    Nginx -->|Routes| AdminUI
    
    GameUI -->|POST question| ChatAPI
    AdminUI -->|Trigger RAG| AdminAPI
    AdminUI -->|Download PDF| AdminAPI
    
    ChatAPI --> RAG
    AdminAPI --> RAG
    
    RAG -->|Orchestrates| PDFProc
    RAG -->|Orchestrates| VectorDB
    RAG -->|Orchestrates| LLMSvc
    RAG -->|Orchestrates| Storage
    
    PDFProc -->|Reads| LocalPDF
    PDFProc -->|Writes| LocalTexts
    
    VectorDB -->|Store/Query| PGLocal
    
    LLMSvc -->|API Call| OpenAI
    
    Storage -->|Local Dev| LocalPDF
    Storage -->|AWS Prod| S3Private
    
    ChatAPI -->|Query/Store| PGLocal
    
    FrontendTask -->|Serves| Browser
    BackendTask -->|Handles API| ChatAPI
    BackendTask -->|IAM Role| IAM
    IAM -->|Access| S3Private
    BackendTask -->|Query| RDSDB
    
    ALB -->|Routes Frontend| FrontendTask
    ALB -->|Routes /api/*| BackendTask
    
    style Browser fill:#e1f5ff
    style GameUI fill:#fff3e0
    style AdminUI fill:#fff3e0
    style ChatAPI fill:#f3e5f5
    style AdminAPI fill:#f3e5f5
    style RAG fill:#e8f5e9
    style PDFProc fill:#e8f5e9
    style VectorDB fill:#e8f5e9
    style LLMSvc fill:#e8f5e9
    style Storage fill:#e8f5e9
    style PGLocal fill:#fce4ec
    style RDSDB fill:#fce4ec
    style S3Private fill:#fce4ec
    style OpenAI fill:#ffe0b2
    style ALB fill:#c8e6c9
    style FrontendTask fill:#c8e6c9
    style BackendTask fill:#c8e6c9
    style IAM fill:#c8e6c9
```

## Nx Monorepo Structure Diagram

```mermaid
graph TD
    Root["📦 Monorepo Root<br/>summary-buddy"]
    
    Root --> Apps["apps/"]
    Root --> Libs["libs/"]
    Root --> Tools["tools/"]
    Root --> Config["Configuration Files<br/>nx.json, workspace.json<br/>package.json, tsconfig.json"]
    Root --> Infra["Infrastructure<br/>docker-compose.yml<br/>terraform/"]
    Root --> Resources["resources/"]
    
    Apps --> Frontend["webui/<br/>React + TypeScript<br/>Nx App"]
    Apps --> Backend["api-server/<br/>Flask + Python<br/>Organized in Nx"]
    
    Frontend --> FrontSrc["src/<br/>components/<br/>pages/<br/>styles/"]
    Frontend --> FrontConfig["package.json<br/>tsconfig.json<br/>.env.example"]
    Frontend --> FrontDocker["Dockerfile<br/>nginx.conf"]
    
    Backend --> BackendApp["app/<br/>api/<br/>services/<br/>models/<br/>db/<br/>utils/"]
    Backend --> BackendConfig["requirements.txt<br/>pyproject.toml<br/>.env.example"]
    Backend --> BackendDocker["Dockerfile<br/>wsgi.py"]
    
    Libs --> SharedTypes["types/<br/>Shared TypeScript types<br/>API contracts"]
    Libs --> SharedConfig["shared/<br/>Shared utilities<br/>configs"]
    
    Tools --> Scripts["scripts/<br/>Build & deploy<br/>scripts"]
    
    Resources --> PDF["uploaded documents (.pdf / .txt)"]
    Resources --> Texts["summary_buddy_texts/"]
    
    style Root fill:#e3f2fd
    style Apps fill:#c8e6c9
    style Libs fill:#fff9c4
    style Tools fill:#ffe0b2
    style Config fill:#f3e5f5
    style Infra fill:#fce4ec
    style Resources fill:#e0f2f1
    style Frontend fill:#a5d6a7
    style Backend fill:#a5d6a7
    style FrontSrc fill:#c8e6c9
    style BackendApp fill:#c8e6c9
    style SharedTypes fill:#fff59d
    style SharedConfig fill:#fff59d
```

## Monorepo Organization

### **apps/** - Nx Applications
Contains the main frontend and backend applications managed by Nx:

#### **webui/**
- React + TypeScript application
- Built and served by Nx
- Dependencies managed in root `package.json`
- Contains all UI components and pages

#### **api-server/**
- Flask + Python application
- Organized under Nx workspace structure (non-npm)
- Dependencies in `requirements.txt`
- Python package structured as `app/` module

### **libs/** - Shared Code
Reusable code and configurations:

#### **types/**
- TypeScript type definitions
- Shared API contracts between frontend and backend
- Request/response schemas

#### **shared/**
- Common utilities
- Configuration templates
- Helper functions

### **tools/** - Build & Deployment Scripts
- Custom build scripts
- Docker build helpers
- Deployment automation

### **Configuration Files**
- **nx.json**: Nx workspace configuration
- **workspace.json**: Project definitions
- **package.json**: Root monorepo dependencies and scripts
- **tsconfig.json**: Root TypeScript configuration

### **Infrastructure & Resources**
- **docker-compose.yml**: Local development orchestration
- **terraform/**: AWS infrastructure as code
- **resources/**: PDF and extracted text files

## Nx CLI Commands

```bash
# Development
nx serve frontend                    # Start React dev server
nx build frontend                    # Build React app
nx lint frontend                     # Lint frontend code
nx test frontend                     # Test frontend

# Viewing project graph
nx graph                             # Visualize monorepo dependencies
nx affected:graph --base=main        # Show affected projects

# Backend commands (custom)
nx run backend:lint                  # Custom Python linting
nx run backend:test                  # Custom Python tests
```

## Architecture Components

### Frontend Layer
- **React + TypeScript**: Type-safe UI components
- **Game Master Chat** (`/game-master-chatbot`): Main chat interface
- **Admin Panel** (`/admin`): Administrative controls

### API Layer (Flask Backend)
- **POST /api/ask-game-master-chatbot**: Submit questions and receive RAG-enhanced answers
- **GET /api/admin/download-pdf**: Download an uploaded document
- **POST /api/admin/run-rag-pipeline**: Trigger PDF processing and vector DB creation
- **GET /api/health**: Health check endpoint

### Backend Services

#### RAG Pipeline Orchestrator
Coordinates the entire retrieval-augmented generation workflow:
- PDF processing
- Text chunking and embedding
- Vector database operations
- LLM query handling

#### PDF Processor Service
- Extracts text from PDF using `pypdf`
- Generates individual page text files
- Stores texts in local Docker volume (dev) or S3 (prod)

#### Vector DB Service
- Creates embeddings using OpenAI's text-embedding-3-large
- Manages the pgvector vector store inside PostgreSQL
- Handles similarity search queries

#### LLM Service
- Integrates with OpenAI GPT-4
- Generates context-aware responses
- Manages conversation context

#### Storage Service
- **Local Development**: Reads/writes to Docker volumes
- **AWS Production**: Interfaces with private S3 bucket

### Data Layer

#### Local Development
- **PostgreSQL + pgvector**: Conversation history, metadata, and embeddings
- **PDF & Text Files**: Stored on Docker volumes

#### AWS Production
- **RDS PostgreSQL**: Multi-AZ for high availability
- **S3 Bucket**: Private bucket with strict IAM policies
  - Backend IAM role has exclusive access
  - Public access blocked
  - Versioning enabled for recovery

### External Services
- **OpenAI API**: GPT-4 chat completions and embeddings

### AWS Infrastructure (Production)
- **ALB**: Routes traffic to frontend and backend services
- **ECS Fargate Tasks**: Auto-scaled containerized services
- **IAM Role**: Backend service has scoped permissions for S3

## Data Flow

### Chat Request Flow
1. User enters question in Game Master Chat
2. Frontend sends POST to `/api/ask-game-master-chatbot`
3. Backend RAG pipeline retrieves similar documents from pgvector
4. LLM generates answer with retrieved context
5. Backend stores conversation in PostgreSQL
6. Response returned to frontend

### RAG Pipeline Initialization
1. Admin clicks "Run RAG Pipeline"
2. Backend checks S3/local storage for PDF
3. PDF Processor extracts text pages
4. Text splitter chunks content
5. Embeddings generated via OpenAI
6. pgvector tables in PostgreSQL created/updated
7. Status returned to admin

## Security Considerations

- **S3 Bucket**: Private with bucket policies blocking public access
- **IAM Policies**: Backend service has scoped, least-privilege permissions
- **VPC**: All AWS resources in private subnets except ALB
- **Environment Variables**: Sensitive credentials in AWS Secrets Manager
- **Database**: RDS in private subnet, no public endpoint

## Deployment Environments

### Local Development
```bash
docker-compose up -d
# All services run locally with Docker volumes
```

### AWS Production
```bash
terraform apply
# Infrastructure provisioned: ECS, RDS, S3, ALB, VPC
```
