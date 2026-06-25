# Summary Buddy Chatbot - Frontend

React + TypeScript frontend for the Summary Buddy Chatbot with RAG capabilities.

## Features

### 🎮 Game Master Chat Page (`/game-master-chatbot`)
- Ask questions about your uploaded documents
- RAG-powered responses with source citations
- Conversation history with load/replay functionality
- Real-time loading states with skeleton animations
- Source references displayed with relevance
- Conversation tracking with unique IDs
- Clear individual questions or entire history

### ⚙️ Admin Panel Page (`/admin`)
- **PDF Management**: Download an uploaded PDF
- **RAG Pipeline Control**: Process PDFs and create vector database
- **Pipeline Status Monitoring**: 
  - Vector database statistics
  - Last execution details
  - Conversation count tracking
  - Real-time status refresh
- **Interactive Feedback**: Detailed success/error messages with actionable information

### 🎨 UI/UX Features
- Responsive design (mobile, tablet, desktop)
- Dark/gradient backgrounds with modern styling
- Smooth animations and transitions
- Loading skeletons for better perceived performance
- Comprehensive error handling with helpful messages
- Navigation between pages with active indicators
- Professional typography and color scheme

## Project Structure

```
webui/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── App.tsx                 # Main app component with routing
│   ├── index.tsx               # React entry point
│   ├── components/
│   │   ├── GameMasterChat.tsx # Enhanced chat UI component
│   │   │                        # Features: history, sources, loading states
│   │   └── AdminPanel.tsx      # Enhanced admin controls component
│   │                            # Features: status monitoring, pipeline control
│   ├── pages/
│   │   ├── GameMasterPage.tsx # Chat page with header & footer
│   │   └── AdminPage.tsx       # Admin page with header & footer
│   ├── services/
│   │   └── api.ts             # API client with all endpoints
│   ├── types/
│   │   └── index.ts           # TypeScript type definitions
│   └── styles/
│       ├── App.css            # Global styles & CSS variables
│       ├── GameMasterPage.css # Page layout styles
│       ├── AdminPage.css      # Admin page layout styles
│       ├── GameMasterChat.css # Chat component (150+ lines)
│       └── AdminPanel.css     # Admin component (200+ lines)
├── vite.config.ts              # Vite configuration
├── tsconfig.json               # TypeScript configuration
├── tsconfig.node.json          # TypeScript config for Vite
├── package.json                # Dependencies
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pnpm install
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env.local
   ```
   
   The default configuration uses `http://localhost:5000/api` for the backend.

3. **Start development server:**
   ```bash
   pnpm run dev
   ```
   
   Frontend will be available at `http://localhost:3000`

### Docker Development

1. **Start with docker-compose:**
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```
   
   Frontend will be available at `http://localhost:3000`

2. **Rebuild after changes:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

## Available Scripts

```bash
# Start development server with hot reload
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview

# Type check with TypeScript
pnpm run type-check

# Lint with ESLint (if configured)
pnpm run lint
```

## Environment Variables

Create `.env.local` file:

```env
# Backend API configuration
VITE_API_BASE_URL=http://localhost:5000/api
```

## Page Routes

| Route | Component | Purpose |
|-------|-----------|---------|
| `/` | GameMasterPage | Default route to chat |
| `/game-master-chatbot` | GameMasterPage | Chat with the Game Master |
| `/admin` | AdminPage | Admin controls and monitoring |

## Components

### GameMasterChat
**File**: `src/components/GameMasterChat.tsx`

Features:
- Question input with Ctrl+Enter shortcut
- Answer display with formatting
- Source citations (clickable in future versions)
- Conversation history with timestamps
- Load previous conversations
- Clear individual responses or entire history
- Loading skeleton animation
- Error handling with user-friendly messages

**State Management**:
```typescript
- question: string              // Current question
- answer: string                // Current answer
- sources: string[]             // Answer sources
- loading: boolean              // Loading state
- error: string                 // Error message
- conversations: array          // History of Q&A
- showHistory: boolean          // Show/hide history
```

### AdminPanel
**File**: `src/components/AdminPanel.tsx`

Features:
- PDF download button
- RAG pipeline trigger
- Real-time pipeline status monitoring
- Status refresh button (manual or auto-polling every 30s)
- Vector database statistics
- Last execution details with timestamps
- Conversation count display
- Helpful instructions

**Monitoring Data**:
```typescript
- Vector DB status and document count
- Last execution status and timestamps
- Total conversation count
- Real-time auto-refresh every 30 seconds
```

## API Integration

All API calls go through `src/services/api.ts` using Axios:

```typescript
// Ask a question
askGameMaster(question: string) → ChatResponse

// Run RAG pipeline
runRAGPipeline() → RAGPipelineResponse

// Get pipeline status
getPipelineStatus() → PipelineStatus

// Download PDF
downloadPDF() → void (triggers download)
```

## Styling

### CSS Architecture
- **Global variables** in `App.css`:
  - Colors: primary, secondary, success, error, warning
  - Spacing, shadows, transitions
  
- **Page layouts** in `GameMasterPage.css` and `AdminPage.css`:
  - Header with navigation
  - Responsive content area
  - Footer

- **Component styles**:
  - `GameMasterChat.css` (150+ lines): Chat UI, history, sources
  - `AdminPanel.css` (200+ lines): Controls, status cards, monitoring

### Responsive Design
- Mobile: < 768px (single column, full-width buttons)
- Tablet: 768px - 1024px (optimized layout)
- Desktop: > 1024px (full features, multi-column grids)

## Type Definitions

**File**: `src/types/index.ts`

```typescript
interface ChatResponse {
  answer: string
  sources: string[]
  conversation_id?: string
}

interface RAGPipelineResponse {
  status: 'completed' | 'failed'
  chunks_created?: number
  pages_processed?: number
  message?: string
  error?: string
}

interface ConversationMessage {
  id: string
  question: string
  answer: string
  sources: string[]
  timestamp: Date
}
```

## Performance Optimizations

- **Vite**: Fast build tool with hot module replacement
- **React 18**: Concurrent rendering and automatic batching
- **TypeScript**: Type safety without runtime overhead
- **CSS**: Minimal CSS with CSS variables for theming
- **API Caching**: Results stored in component state
- **Lazy Loading**: History panel loads on demand
- **Skeleton Loading**: Visual feedback during API calls

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: Latest 2 versions
- Mobile: iOS Safari, Chrome Mobile

## Troubleshooting

### Frontend won't connect to backend
- Check backend is running: `curl http://localhost:5000/api/health`
- Verify `VITE_API_BASE_URL` in `.env.local`
- Check CORS headers in browser console

### Styles not loading
- Clear browser cache and rebuild: `pnpm run build`
- Check that CSS files are imported in components

### TypeScript errors
- Run type check: `pnpm run type-check`
- Ensure `tsconfig.json` is properly configured

### Hot reload not working
- Ensure Vite dev server is running: `pnpm run dev`
- Check port 3000 is not in use
- Restart dev server if needed

## Development Workflow

1. **Start dev server**: `pnpm run dev`
2. **Make changes** to TypeScript/CSS files
3. **Hot reload** automatically applies changes
4. **Test** in browser at `http://localhost:3000`
5. **Build** for production: `pnpm run build`

## Deployment

### Docker Production Build
```bash
docker build -f webui/Dockerfile -t summary-buddy-frontend:latest webui/
docker run -p 80:80 summary-buddy-frontend:latest
```

### Static Build
```bash
pnpm run build
# Output in dist/ directory
# Serve with any static server or CDN
```

## Resources

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [Vite Documentation](https://vitejs.dev)
- [Axios Documentation](https://axios-http.com)
- [Backend API Documentation](../api-server/API_ENDPOINTS.md)

## License

MIT - See LICENSE file in project root
   ```

3. **Start development server:**
   ```bash
   pnpm run dev
   ```

   Server will be available at `http://localhost:3000`

### Docker Development

```bash
docker-compose up frontend
```

## Available Scripts

```bash
# Start development server
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview

# Run tests
pnpm run test

# Run tests with UI
pnpm run test:ui

# Type check
pnpm lint
```

## Features

### Game Master Chat Page (`/game-master-chatbot`)
- Text area to ask questions
- Read-only text area displaying Game Master responses
- Sources attribution
- Conversation history tracking
- Error handling and loading states

### Admin Panel (`/admin`)
- Download PDF button (uploaded document)
- Run RAG Pipeline button
  - Converts PDF to text files
  - Generates embeddings
  - Creates/updates vector database
- Real-time status updates
- Success/error notifications

## API Integration

The frontend communicates with the backend via REST API:

### Endpoints Used
- **POST** `/api/ask-ai-summary-buddy` - Ask a question
- **GET** `/api/admin/download-pdf` - Download PDF
- **POST** `/api/admin/upload-documents` - Upload and process documents
- **GET** `/api/health` - Health check

API client is in `src/services/api.ts`

## Styling

- **CSS-in-files** approach with modular CSS files
- **Responsive design** for mobile and desktop
- **Gradient backgrounds** and smooth transitions
- **Dark mode friendly** color scheme

### Color Scheme
- Primary: `#1e3a8a` (Dark Blue)
- Secondary: `#3b82f6` (Bright Blue)
- Success: `#10b981` (Green)
- Error: `#ef4444` (Red)

## Technologies

- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **React Router v6**: Client-side routing
- **Axios**: HTTP client
- **CSS**: Styling (no framework, vanilla CSS)

## Environment Variables

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:5000/api

# Server Port
VITE_PORT=3000
```

## Development Workflow

1. Components are co-located with their styles
2. Type definitions in `src/types/`
3. API calls centralized in `src/services/api.ts`
4. Pages handle routing and layout
5. Reusable components in `src/components/`

## Production Build

```bash
pnpm run build
```

Outputs to `dist/` directory. Can be served by Nginx or any static file server.

### Nginx Configuration Example
```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
    }
}
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Modern mobile browsers

## Troubleshooting

### CORS Issues
Ensure backend has CORS enabled and frontend API URL is correct in `.env`

### API Connection Failed
Check backend is running on the correct port (default: 5000)

### Build Errors
Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
pnpm install
```

## TODO

- [ ] Add conversation history view
- [ ] Implement real-time updates with WebSockets
- [ ] Add dark mode toggle
- [ ] Add analytics tracking
- [ ] Improve error messages
- [ ] Add loading skeleton screens
- [ ] Implement pagination for chat history

## References

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)

