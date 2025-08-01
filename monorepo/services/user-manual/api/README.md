# API Reference

Complete API documentation for all services in the Claude Code Monorepo system.

## 📋 Service Overview

| Service | Port | Base URL | Protocol | Status |
|---------|------|----------|----------|--------|
| ClaudeCodeUI Backend | 3000 | http://localhost:3000 | REST | ✅ |
| CLI Analytics | 3001 | http://localhost:3001 | REST + WebSocket | ✅ |
| SuperClaude Framework | 8001 | http://localhost:8001 | REST | ✅ |
| GenAI Stack | 8003 | http://localhost:8003 | REST | ✅ |
| Memory Service | 8500 | http://localhost:8500 | REST | ✅ |
| Unified Query Service | 8505 | http://localhost:8505 | REST + WebSocket | 🚧 |
| n8n Automation | 5678 | http://localhost:5678 | REST + UI | ✅ |
| Ollama | 11434 | http://localhost:11434 | REST | ✅ |

## 🚀 ClaudeCodeUI Backend API (Port 3000)

Main application backend providing authentication, project management, and git operations.

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com"
  }
}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

#### Status Check
```http
GET /api/auth/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "authenticated": true,
  "user": {
    "id": 1,
    "username": "user"
  }
}
```

### Project Management

#### List Projects
```http
GET /api/projects
Authorization: Bearer <token>
```

**Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "name": "My Project",
      "path": "/path/to/project",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Project
```http
POST /api/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Project",
  "path": "/path/to/new/project",
  "description": "Project description"
}
```

#### Get Project
```http
GET /api/projects/:id
Authorization: Bearer <token>
```

#### Update Project
```http
PUT /api/projects/:id
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Project",
  "description": "Updated description"
}
```

#### Delete Project
```http
DELETE /api/projects/:id
Authorization: Bearer <token>
```

### Git Operations

#### Git Status
```http
GET /api/git/:project/status
Authorization: Bearer <token>
```

**Response:**
```json
{
  "branch": "main",
  "ahead": 0,
  "behind": 0,
  "staged": [],
  "unstaged": ["file1.js", "file2.js"],
  "untracked": ["newfile.js"]
}
```

#### Commit Changes
```http
POST /api/git/:project/commit
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Commit message",
  "files": ["file1.js", "file2.js"]
}
```

#### Push Changes
```http
POST /api/git/:project/push
Authorization: Bearer <token>
Content-Type: application/json

{
  "branch": "main",
  "remote": "origin"
}
```

#### Pull Changes
```http
POST /api/git/:project/pull
Authorization: Bearer <token>
Content-Type: application/json

{
  "branch": "main",
  "remote": "origin"
}
```

### File Operations

#### List Files
```http
GET /api/files/:project
Authorization: Bearer <token>
Query Parameters:
  - path: /optional/subdirectory
  - depth: 3 (default)
```

#### Read File
```http
GET /api/files/:project/content
Authorization: Bearer <token>
Query Parameters:
  - path: /path/to/file.js (required)
```

#### Write File
```http
POST /api/files/:project/content
Authorization: Bearer <token>
Content-Type: application/json

{
  "path": "/path/to/file.js",
  "content": "file content here"
}
```

### MCP Server Integration

#### List Available Servers
```http
GET /api/mcp/servers
Authorization: Bearer <token>
```

#### Server Status
```http
GET /api/mcp/servers/:name/status
Authorization: Bearer <token>
```

#### Execute MCP Tool
```http
POST /api/mcp/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "server": "context7",
  "tool": "get-library-docs",
  "arguments": {
    "library_id": "/mongodb/docs"
  }
}
```

## 📊 CLI Analytics API (Port 3001)

Real-time analytics and monitoring for Claude Code sessions.

### Analytics Data

#### Get Sessions
```http
GET /api/analytics/sessions
Query Parameters:
  - limit: 50 (default)
  - offset: 0 (default)
  - status: active|completed|all (default: all)
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_123",
      "status": "active",
      "start_time": "2024-01-01T10:00:00Z",
      "duration": 1800,
      "tokens_used": 5000,
      "project_path": "/path/to/project"
    }
  ],
  "total": 25,
  "page": 1
}
```

#### Get Conversations
```http
GET /api/analytics/conversations
Query Parameters:
  - session_id: session_123 (optional)
  - limit: 20 (default)
  - include_content: true|false (default: false)
```

#### Get Metrics
```http
GET /api/analytics/metrics
Query Parameters:
  - period: 1h|1d|1w|1m (default: 1d)
  - metric_type: tokens|sessions|performance (default: all)
```

**Response:**
```json
{
  "period": "1d",
  "metrics": {
    "total_sessions": 15,
    "total_tokens": 75000,
    "avg_session_duration": 1200,
    "success_rate": 0.95,
    "error_count": 2
  },
  "timeseries": [
    {
      "timestamp": "2024-01-01T00:00:00Z",
      "sessions": 3,
      "tokens": 15000
    }
  ]
}
```

#### Export Data
```http
GET /api/analytics/export
Authorization: Bearer <token>
Query Parameters:
  - format: csv|json (default: json)
  - type: sessions|conversations|metrics (default: sessions)
  - start_date: 2024-01-01 (optional)
  - end_date: 2024-01-31 (optional)
```

### Health & System Info

#### Health Check
```http
GET /api/health
```

#### System Information
```http
GET /api/system/info
```

**Response:**
```json
{
  "version": "1.0.0",
  "uptime": 86400,
  "memory_usage": {
    "used": 150000000,
    "total": 1000000000
  },
  "cpu_usage": 0.25,
  "active_processes": 5
}
```

### WebSocket API

#### Real-time Updates
```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:3001/ws/analytics');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
  // Types: session_update, conversation_update, metrics_update
};
```

#### Notifications
```javascript
// Connect to notifications
const ws = new WebSocket('ws://localhost:3001/ws/notifications');

ws.onopen = () => {
  // Subscribe to specific events
  ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['claude_waiting', 'session_ended', 'error_occurred']
  }));
};
```

## 🤖 SuperClaude Framework API (Port 8001)

Enhanced AI framework with personas and specialized commands.

### Framework Status

#### Health Check
```http
GET /health
```

#### Framework Info
```http
GET /api/framework/info
```

**Response:**
```json
{
  "version": "3.0.0",
  "commands_available": 16,
  "personas_loaded": 11,
  "mcp_servers": ["context7", "sequential", "magic", "playwright"],
  "status": "ready"
}
```

### Command Execution

#### Execute Command
```http
POST /api/commands/execute
Content-Type: application/json

{
  "command": "sc:implement",
  "args": "user authentication system",
  "flags": ["--persona-backend", "--validate"],
  "context": {
    "project_path": "/path/to/project",
    "files": ["src/app.js", "src/auth.js"]
  }
}
```

**Response:**
```json
{
  "command_id": "cmd_123",
  "status": "executing",
  "persona_activated": "backend",
  "estimated_duration": 300,
  "mcp_servers_used": ["context7", "sequential"]
}
```

#### Get Command Status
```http
GET /api/commands/:command_id/status
```

#### Cancel Command
```http
POST /api/commands/:command_id/cancel
```

### Persona Management

#### List Personas
```http
GET /api/personas
```

**Response:**
```json
{
  "personas": [
    {
      "name": "architect",
      "description": "Systems architecture specialist",
      "specialties": ["design", "scalability", "patterns"],
      "auto_activation_triggers": ["architecture", "design", "scale"]
    }
  ]
}
```

#### Get Persona Details
```http
GET /api/personas/:name
```

#### Activate Persona
```http
POST /api/personas/:name/activate
Content-Type: application/json

{
  "context": "working on microservices architecture",
  "priority": "high"
}
```

### MCP Server Integration

#### List MCP Servers
```http
GET /api/mcp/servers
```

#### Server Health Check
```http
GET /api/mcp/servers/:name/health
```

#### Execute MCP Tool
```http
POST /api/mcp/execute
Content-Type: application/json

{
  "server": "context7",
  "tool": "resolve-library-id",
  "arguments": {
    "libraryName": "react"
  }
}
```

## 🧠 Memory Service API (Port 8500)

Integration layer for Cognee and Memento MCP memory systems.

### Health & Status

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Memory Integration Service",
  "components": {
    "cognee": "ready",
    "memento-mcp": "ready",
    "neo4j": "connected"
  }
}
```

### Memory Operations

#### Store Memory
```http
POST /api/memory/store
Content-Type: application/json

{
  "content": "User authentication patterns and best practices",
  "metadata": {
    "type": "knowledge",
    "tags": ["auth", "security", "patterns"],
    "source": "documentation"
  },
  "system": "cognee"
}
```

#### Query Memory
```http
POST /api/memory/query
Content-Type: application/json

{
  "query": "authentication security patterns",
  "system": "all",
  "options": {
    "max_results": 10,
    "include_metadata": true
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "JWT authentication with refresh tokens...",
      "metadata": {
        "relevance_score": 0.95,
        "source": "cognee",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  ],
  "total_results": 1,
  "query_time_ms": 150
}
```

#### Get Memory Status
```http
GET /api/memory/status
```

### System-Specific Endpoints

#### Cognee Operations
```http
# Store in Cognee specifically
POST /api/memory/cognee/store

# Query Cognee graph
POST /api/memory/cognee/graph_query
{
  "query": "MATCH (n:Concept {name: 'authentication'}) RETURN n",
  "parameters": {}
}
```

#### Memento MCP Operations
```http
# Key-value storage
POST /api/memory/memento/set
{
  "key": "auth_patterns",
  "value": "JWT with refresh tokens",
  "metadata": {"type": "pattern"}
}

# Key-value retrieval
GET /api/memory/memento/get/:key
```

## 🔄 Unified Query Service API (Port 8505)

Multi-memory system orchestration with document processing and workflows.

### Query Operations

#### Unified Query
```http
POST /api/query
Content-Type: application/json

{
  "query": "React component optimization techniques",
  "mode": "unified",
  "sources": ["cognee", "memento", "memos", "llamacloud"],
  "options": {
    "max_results": 20,
    "include_metadata": true,
    "ranking_strategy": "hybrid"
  }
}
```

**Response:**
```json
{
  "query_id": "query_123",
  "mode": "unified",
  "results": [
    {
      "content": "React.memo can prevent unnecessary re-renders...",
      "source": "cognee",
      "relevance_score": 0.95,
      "metadata": {
        "type": "code_snippet",
        "language": "javascript"
      }
    }
  ],
  "total_results": 15,
  "query_time_ms": 250,
  "sources_queried": ["cognee", "memos", "llamacloud"]
}
```

#### Sequential Query
```http
POST /api/query
Content-Type: application/json

{
  "query": "database optimization strategies",
  "mode": "sequential",
  "sources": ["cognee", "memos"],
  "options": {
    "context_building": true,
    "refinement_iterations": 3
  }
}
```

#### Smart Query
```http
POST /api/query
Content-Type: application/json

{
  "query": "how to implement OAuth2 in Node.js",
  "mode": "smart",
  "options": {
    "auto_select_sources": true,
    "intent_analysis": true,
    "explain_routing": true
  }
}
```

### Document Processing

#### Process Document
```http
POST /api/document/process
Content-Type: application/json

{
  "file_path": "/path/to/document.pdf",
  "pipeline": "research",
  "output_format": "markdown",
  "options": {
    "extract_citations": true,
    "fact_checking": true,
    "entity_recognition": true
  },
  "store_in": ["cognee", "memos", "llamacloud"]
}
```

**Response:**
```json
{
  "process_id": "proc_123",
  "status": "processing",
  "estimated_completion": "2024-01-01T10:05:00Z",
  "pipeline": "research",
  "steps": ["parse", "extract_citations", "fact_check", "store"]
}
```

#### Get Processing Status
```http
GET /api/document/process/:process_id/status
```

#### List Processing Jobs
```http
GET /api/document/jobs
Query Parameters:
  - status: pending|processing|completed|failed
  - limit: 20
```

### Workflow Management

#### Deploy Workflow
```http
POST /api/workflow/deploy
Content-Type: application/json

{
  "workflow_id": "memory_sync",
  "config": {
    "sync_interval": "1h",
    "conflict_resolution": "merge",
    "systems": ["cognee", "memos"]
  },
  "triggers": ["schedule"]
}
```

#### List Workflows
```http
GET /api/workflow/list
```

#### Get Workflow Status
```http
GET /api/workflow/:workflow_id/status
```

#### Trigger Workflow
```http
POST /api/workflow/:workflow_id/trigger
```

### System Health

#### Overall Health
```http
GET /health
```

#### Individual System Health
```http
GET /api/systems/health
```

**Response:**
```json
{
  "systems": {
    "cognee": {
      "status": "healthy",
      "response_time_ms": 150,
      "last_check": "2024-01-01T10:00:00Z"
    },
    "memento": {
      "status": "healthy",
      "response_time_ms": 75,
      "last_check": "2024-01-01T10:00:00Z"
    }
  },
  "overall_status": "healthy"
}
```

## 🤖 GenAI Stack API (Port 8003)

AI model stack with Ollama integration for local LLM inference.

### Model Management

#### List Available Models
```http
GET /api/models
```

**Response:**
```json
{
  "models": [
    {
      "name": "llama2",
      "size": "7B",
      "status": "loaded",
      "memory_usage": "4.2GB"
    },
    {
      "name": "codellama",
      "size": "13B", 
      "status": "available",
      "memory_usage": "0GB"
    }
  ]
}
```

#### Load Model
```http
POST /api/models/:name/load
```

#### Unload Model
```http
POST /api/models/:name/unload
```

### Inference

#### Generate Text
```http
POST /api/generate
Content-Type: application/json

{
  "model": "llama2",
  "prompt": "Explain how JWT authentication works",
  "options": {
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }
}
```

**Response:**
```json
{
  "response": "JWT (JSON Web Token) authentication is a stateless...",
  "model": "llama2",
  "tokens_generated": 245,
  "generation_time_ms": 1500
}
```

#### Streaming Generation
```http
POST /api/generate/stream
Content-Type: application/json

{
  "model": "codellama",
  "prompt": "Write a Python function to validate email addresses",
  "stream": true
}
```

### Embeddings

#### Generate Embeddings
```http
POST /api/embeddings
Content-Type: application/json

{
  "model": "all-minilm-l6-v2",
  "text": "React component optimization techniques",
  "normalize": true
}
```

**Response:**
```json
{
  "embedding": [0.1, -0.2, 0.3, ...],
  "dimension": 384,
  "model": "all-minilm-l6-v2"
}
```

### Chat Interface

#### Chat Completion
```http
POST /api/chat
Content-Type: application/json

{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "How do I optimize React performance?"}
  ],
  "options": {
    "temperature": 0.7,
    "max_tokens": 300
  }
}
```

## 🌐 n8n Automation API (Port 5678)

Workflow automation with custom nodes for Claude Code integration.

### Workflow Management

#### List Workflows
```http
GET /api/v1/workflows
Authorization: Bearer <api_key>
```

#### Create Workflow
```http
POST /api/v1/workflows
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "name": "Claude Code Automation",
  "nodes": [...],
  "connections": {...}
}
```

#### Execute Workflow
```http
POST /api/v1/workflows/:id/execute
Authorization: Bearer <api_key>
```

### Custom Nodes

The monorepo includes custom n8n nodes for Claude Code integration:

#### Claude Code Node
- Execute Claude Code commands
- Process responses
- Handle file operations

#### Memory System Node
- Query memory systems
- Store new information
- Manage knowledge graphs

#### Analytics Node
- Collect usage metrics
- Generate reports
- Monitor system health

## 🔄 Ollama API (Port 11434)

Local LLM server for model inference.

### Model Operations

#### List Models
```http
GET /api/tags
```

#### Pull Model
```http
POST /api/pull
Content-Type: application/json

{
  "name": "llama2"
}
```

#### Generate Response
```http
POST /api/generate
Content-Type: application/json

{
  "model": "llama2",
  "prompt": "Write a function to sort an array",
  "stream": false
}
```

## 🛠️ SDK & Client Libraries

### JavaScript SDK

```javascript
// Install
npm install @claude-code/sdk

// Usage
import { ClaudeCodeClient } from '@claude-code/sdk';

const client = new ClaudeCodeClient({
  baseURL: 'http://localhost:3000',
  analyticsURL: 'http://localhost:3001',
  memoryURL: 'http://localhost:8500'
});

// Authenticate
await client.auth.login('username', 'password');

// Execute command with SuperClaude
const result = await client.superClaude.execute('sc:implement', 'user auth', {
  persona: 'backend',
  validate: true
});

// Query memory systems
const memories = await client.memory.query('authentication patterns');

// Get analytics
const metrics = await client.analytics.getMetrics('1d');
```

### Python SDK

```python
# Install
pip install claude-code-sdk

# Usage
from claude_code_sdk import ClaudeCodeClient

client = ClaudeCodeClient(
    base_url="http://localhost:3000",
    analytics_url="http://localhost:3001",
    memory_url="http://localhost:8500"
)

# Authenticate
client.auth.login("username", "password")

# Execute SuperClaude command
result = client.superclaude.execute(
    command="sc:analyze",
    args="security vulnerabilities",
    flags=["--think-hard", "--persona-security"]
)

# Query unified memory
memories = client.unified_query.query({
    "query": "React performance patterns",
    "mode": "unified",
    "sources": ["cognee", "memos"]
})

# Process document
job = client.unified_query.process_document({
    "file_path": "/path/to/doc.pdf",
    "pipeline": "research",
    "store_in": ["cognee", "llamacloud"]
})
```

## 🔐 Authentication & Security

### API Key Authentication

Most services support API key authentication:

```http
Authorization: Bearer <api_key>
# or
X-API-Key: <api_key>
```

### JWT Authentication

ClaudeCodeUI Backend uses JWT tokens:

```http
Authorization: Bearer <jwt_token>
```

### Rate Limiting

APIs implement rate limiting:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```

## 🔍 Error Handling

### Standard Error Format

All APIs return errors in a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "query",
      "reason": "Query cannot be empty"
    },
    "request_id": "req_123"
  }
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error
- `503` - Service Unavailable

## 📊 API Testing

### Using curl

```bash
# Health check
curl http://localhost:3000/api/health

# Authenticated request
curl -H "Authorization: Bearer <token>" \
     http://localhost:3000/api/projects

# POST with JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"name": "Test Project"}' \
     http://localhost:3000/api/projects
```

### Using Postman

Import the API collection:
1. Download collection from `/docs/postman/`
2. Import in Postman
3. Set environment variables
4. Run requests

### Integration Testing

```javascript
// Jest example
describe('ClaudeCode API', () => {
  test('should authenticate user', async () => {
    const response = await fetch('http://localhost:3000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'test',
        password: 'password'
      })
    });
    
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data.token).toBeDefined();
  });
});
```

This API reference provides comprehensive documentation for all services in the Claude Code Monorepo system. Each API includes authentication methods, request/response formats, and practical examples for integration.