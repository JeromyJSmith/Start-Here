# Unified Query Service

The Unified Query Service is a comprehensive query orchestration layer that unifies multiple memory systems (Cognee, Memento MCP, MemOS, LlamaCloud) with advanced document processing and workflow deployment capabilities.

## 📋 Overview

The Unified Query Service acts as the central intelligence layer for memory operations across the monorepo system, providing:

- **Multi-Memory Integration**: Query across Cognee, Memento MCP, MemOS, and LlamaCloud simultaneously
- **Document Processing**: Advanced parsing with LlamaParse integration
- **Workflow Orchestration**: LlamaDeploy integration for production workflows
- **Intelligent Routing**: Smart query distribution based on content type and intent
- **Result Aggregation**: Unified results with deduplication and ranking

## 🏗️ Architecture

### System Design

```
Unified Query Service (Port 8505)
├── Query Orchestrator     # Request routing and coordination
├── Document Processor     # LlamaParse integration and pipelines
├── Workflow Engine        # LlamaDeploy workflow management
├── Memory Adapters        # Individual system connectors
│   ├── CogneeAdapter      # Semantic graph queries
│   ├── MementoAdapter     # Key-value memory access
│   ├── MemOSAdapter       # Multi-type memory operations
│   └── LlamaCloudAdapter  # Document index queries
├── Ranking Engine         # Result scoring and ordering
└── Cache Layer           # Performance optimization
```

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│        (Claude Code, APIs, Web UI, CLI)                     │
└─────────────────┬───────────────────────┬──────────────────┘
                  │                       │
                  ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Unified Query Service (Port 8505)              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Query     │  │   Document   │  │    Workflow     │   │
│  │ Orchestrator│  │  Processor   │  │    Engine       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│              Memory System Adapters                          │
│  ┌──────┐ ┌────────┐ ┌───────┐ ┌────────────┐            │
│  │Cognee│ │Memento │ │MemOS  │ │LlamaCloud  │            │
│  └──────┘ └────────┘ └───────┘ └────────────┘            │
└─────────────────┬───────────────────────┬──────────────────┘
                  │                       │
                  ▼                       ▼
         ┌───────────────┐       ┌──────────────┐
         │    Neo4j      │       │  LlamaCloud  │
         │   Database    │       │    Index     │
         └───────────────┘       └──────────────┘
```

## 🚀 Getting Started

### Starting the Service

The Unified Query Service is included in the monorepo setup:

```bash
# Start all services including UQS
make dev

# Start UQS specifically
docker-compose up unified-query-service

# Check service health
curl http://localhost:8505/health
```

### Basic Configuration

Environment variables in `.env`:

```env
# Unified Query Service
UQS_PORT=8505
UQS_DEBUG=true

# Memory System Connections
COGNEE_URL=http://cognee:8080
MEMENTO_URL=http://memento-mcp:3000
MEMOS_URL=http://memos:8000
LLAMACLOUD_API_KEY=your_llamacloud_key

# LlamaParse Integration
LLAMA_INDEX_API_KEY=your_llamaindex_key

# Redis for caching
REDIS_URL=redis://redis:6379

# Neo4j for graph operations
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## 💡 Basic Usage

### Query Endpoints

#### Unified Query

Query all memory systems simultaneously:

```bash
POST http://localhost:8505/api/query
Content-Type: application/json

{
  "query": "user authentication best practices",
  "mode": "unified",
  "sources": ["cognee", "memento", "memos", "llamacloud"],
  "options": {
    "max_results": 10,
    "include_metadata": true,
    "ranking_strategy": "relevance"
  }
}
```

#### Sequential Query

Build context progressively:

```bash
POST http://localhost:8505/api/query
Content-Type: application/json

{
  "query": "secure password storage",
  "mode": "sequential",
  "sources": ["cognee", "memos", "llamacloud"],
  "options": {
    "context_building": true,
    "refinement_iterations": 3
  }
}
```

#### Smart Query

Automatic system selection:

```bash
POST http://localhost:8505/api/query
Content-Type: application/json

{
  "query": "React component optimization techniques",
  "mode": "smart",
  "options": {
    "auto_select_sources": true,
    "intent_analysis": true
  }
}
```

### Document Processing

#### Basic Document Processing

```bash
POST http://localhost:8505/api/document/process
Content-Type: application/json

{
  "file_path": "/path/to/document.pdf",
  "pipeline": "default",
  "output_format": "markdown",
  "store_in": ["cognee", "memos"]
}
```

#### Custom Pipeline Processing

```bash
POST http://localhost:8505/api/document/process
Content-Type: application/json

{
  "file_path": "/path/to/code_documentation.md",
  "pipeline": "code",
  "options": {
    "extract_code_blocks": true,
    "generate_embeddings": true,
    "detect_dependencies": true
  },
  "store_in": ["cognee", "llamacloud"]
}
```

## 🔧 Advanced Features

### Query Modes

#### 1. Unified Mode
- Queries all systems in parallel
- Merges and deduplicates results
- Returns single ranked list

```python
# Python client example
import requests

response = requests.post('http://localhost:8505/api/query', json={
    'query': 'machine learning deployment patterns',
    'mode': 'unified',
    'sources': ['cognee', 'memos', 'llamacloud'],
    'options': {
        'max_results': 20,
        'include_metadata': True,
        'ranking_strategy': 'hybrid'
    }
})

results = response.json()
```

#### 2. Sequential Mode
- Queries systems in order
- Uses previous results to refine next query
- Builds context progressively

```javascript
// JavaScript client example
const response = await fetch('http://localhost:8505/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        query: 'database optimization strategies',
        mode: 'sequential',
        sources: ['cognee', 'memos'],
        options: {
            context_building: true,
            refinement_iterations: 2
        }
    })
});

const data = await response.json();
```

#### 3. Parallel Mode
- Queries all systems simultaneously
- Returns results grouped by source
- No deduplication or ranking

```bash
curl -X POST http://localhost:8505/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "API security vulnerabilities",
    "mode": "parallel",
    "sources": ["cognee", "memento", "memos"],
    "options": {
      "preserve_source_identity": true,
      "include_timing": true
    }
  }'
```

#### 4. Smart Mode
- Analyzes query intent
- Selects optimal systems automatically
- Applies appropriate strategy

```bash
curl -X POST http://localhost:8505/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how to implement OAuth2 in Node.js",
    "mode": "smart",
    "options": {
      "auto_optimize": true,
      "explain_routing": true
    }
  }'
```

### Document Processing Pipelines

#### Default Pipeline
1. **Parse**: LlamaParse extracts content
2. **Chunk**: Intelligent text segmentation
3. **Embed**: Generate embeddings
4. **Enrich**: Add metadata and context
5. **Store**: Distribute to memory systems

#### Custom Pipelines

**Research Pipeline**:
```bash
POST http://localhost:8505/api/document/process
{
  "file_path": "/research/paper.pdf",
  "pipeline": "research",
  "options": {
    "extract_citations": true,
    "fact_checking": true,
    "entity_recognition": true
  }
}
```

**Code Pipeline**:
```bash
POST http://localhost:8505/api/document/process
{
  "file_path": "/docs/api_documentation.md",
  "pipeline": "code",
  "options": {
    "syntax_highlighting": true,
    "dependency_analysis": true,
    "generate_examples": true
  }
}
```

**Legal Pipeline**:
```bash
POST http://localhost:8505/api/document/process
{
  "file_path": "/contracts/terms.pdf",
  "pipeline": "legal",
  "options": {
    "clause_extraction": true,
    "compliance_checking": true,
    "risk_assessment": true
  }
}
```

## 🔄 Workflow Management

### Pre-built Workflows

#### 1. Memory Sync Workflow
Synchronizes data across all memory systems:

```bash
POST http://localhost:8505/api/workflow/deploy
{
  "workflow_id": "memory_sync",
  "config": {
    "sync_interval": "1h",
    "conflict_resolution": "merge",
    "backup_before_sync": true
  },
  "triggers": ["schedule"]
}
```

#### 2. Document Ingestion Workflow
Monitors and processes new documents:

```bash
POST http://localhost:8505/api/workflow/deploy
{
  "workflow_id": "document_ingestion",
  "config": {
    "watch_directories": ["/docs", "/uploads"],
    "auto_process": true,
    "notification_webhook": "http://localhost:3000/webhooks/documents"
  },
  "triggers": ["event"]
}
```

#### 3. Query Enhancement Workflow
Learns and improves query patterns:

```bash
POST http://localhost:8505/api/workflow/deploy
{
  "workflow_id": "query_enhancement",
  "config": {
    "learning_enabled": true,
    "feedback_collection": true,
    "suggestion_generation": true
  },
  "triggers": ["manual", "schedule"]
}
```

### Custom Workflows

Create custom workflows using LlamaDeploy:

```python
# example_workflow.py
from llama_deploy import Workflow, ServiceComponent

workflow = Workflow("custom_analysis")

# Define workflow steps
@workflow.step
async def analyze_content(content: str):
    # Custom analysis logic
    return analyzed_data

@workflow.step  
async def store_results(data: dict):
    # Store in multiple memory systems
    return storage_results

# Deploy workflow
workflow.deploy("http://localhost:8505/api/workflow/deploy")
```

## 📊 Monitoring & Analytics

### Health Monitoring

```bash
# Service health check
GET http://localhost:8505/health

# Individual system health
GET http://localhost:8505/api/systems/health

# Performance metrics
GET http://localhost:8505/api/metrics
```

### Query Analytics

```bash
# Query performance stats
GET http://localhost:8505/api/analytics/queries

# System usage statistics
GET http://localhost:8505/api/analytics/usage

# Error tracking
GET http://localhost:8505/api/analytics/errors
```

### Real-time Monitoring

WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8505/ws/monitoring');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};
```

## 🔧 Configuration

### Service Configuration

Create `config/unified_query_service.yaml`:

```yaml
unified_query_service:
  port: 8505
  debug: true
  
  memory_systems:
    cognee:
      enabled: true
      url: "http://cognee:8080"
      weight: 0.3
      timeout: "5s"
      retry_attempts: 3
    
    memento:
      enabled: true
      url: "http://memento-mcp:3000"
      weight: 0.2
      timeout: "3s"
      retry_attempts: 2
    
    memos:
      enabled: true
      url: "http://memos:8000"
      weight: 0.3
      timeout: "5s"
      retry_attempts: 3
    
    llamacloud:
      enabled: true
      api_key: "${LLAMACLOUD_API_KEY}"
      weight: 0.2
      timeout: "10s"
      retry_attempts: 2

  document_processing:
    llamaparse:
      api_key: "${LLAMA_INDEX_API_KEY}"
      parsing_instruction: "Extract all information preserving structure"
      premium_mode: true
    
    pipelines:
      - name: "default"
        steps: ["parse", "chunk", "embed", "enrich", "store"]
      - name: "research"
        steps: ["parse", "extract_citations", "fact_check", "embed", "store"]
      - name: "code"
        steps: ["parse", "syntax_highlight", "extract_deps", "embed", "store"]
    
    storage:
      batch_size: 100
      parallel_workers: 4
      default_format: "markdown"

  workflows:
    llama_deploy:
      control_plane_port: 8000
      service_port_range: [8001, 8010]
      max_concurrent_workflows: 10
    
    enabled_workflows:
      - "memory_sync"
      - "document_ingestion"
      - "query_enhancement"
      - "maintenance"

  caching:
    enabled: true
    redis_url: "${REDIS_URL}"
    ttl:
      query_results: "1h"
      document_content: "24h"
      embeddings: "7d"
    
  ranking:
    default_strategy: "hybrid"
    strategies:
      relevance:
        semantic_weight: 0.7
        keyword_weight: 0.3
      recency:
        time_decay_factor: 0.1
      hybrid:
        relevance_weight: 0.6
        recency_weight: 0.2
        popularity_weight: 0.2

  performance:
    max_concurrent_queries: 50
    query_timeout: "30s"
    memory_limit: "2GB"
    cpu_limit: "2.0"
```

### Memory System Configuration

Individual adapter configurations:

```yaml
# Cognee Adapter
cognee_adapter:
  graph_queries: true
  semantic_search: true
  relationship_traversal: 3  # max depth
  cache_results: true

# Memento Adapter  
memento_adapter:
  key_value_access: true
  temporal_queries: true
  version_history: true
  compression: "gzip"

# MemOS Adapter
memos_adapter:
  multi_type_support: true
  conversation_context: true
  learning_enabled: true
  personalization: true

# LlamaCloud Adapter
llamacloud_adapter:
  document_indexing: true
  vector_search: true
  hybrid_search: true
  result_reranking: true
```

## 🛠️ Development

### Local Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd monorepo

# Start development environment
make dev

# Access UQS logs
make logs-unified-query-service

# Shell access
make shell-unified-query-service
```

### Testing

```bash
# Run UQS tests
docker-compose exec unified-query-service python -m pytest

# Integration tests
docker-compose exec unified-query-service python -m pytest tests/integration/

# Performance tests
docker-compose exec unified-query-service python -m pytest tests/performance/
```

### Custom Adapter Development

Create custom memory system adapters:

```python
# custom_adapter.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MemorySystemAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict]:
        """Search the memory system"""
        pass
    
    @abstractmethod
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store content in the memory system"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the memory system is healthy"""
        pass

class CustomAdapter(MemorySystemAdapter):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Initialize your custom memory system connection
    
    async def search(self, query: str, options: Dict[str, Any]) -> List[Dict]:
        # Implement search logic for your system
        results = []
        # ... search implementation
        return results
    
    async def store(self, content: str, metadata: Dict[str, Any]) -> str:
        # Implement storage logic
        storage_id = "custom_id"
        # ... storage implementation
        return storage_id
    
    async def health_check(self) -> bool:
        # Check system health
        return True

# Register the adapter
from unified_query_service.adapters import register_adapter
register_adapter("custom", CustomAdapter)
```

## 📚 Examples

### Example 1: Research Assistant

```python
import requests
import json

class ResearchAssistant:
    def __init__(self):
        self.base_url = "http://localhost:8505"
    
    def research_topic(self, topic: str):
        """Research a topic across all memory systems"""
        response = requests.post(f"{self.base_url}/api/query", json={
            "query": f"comprehensive research on {topic}",
            "mode": "unified",
            "sources": ["cognee", "memos", "llamacloud"],
            "options": {
                "max_results": 50,
                "include_metadata": True,
                "ranking_strategy": "relevance"
            }
        })
        
        return response.json()
    
    def process_document(self, file_path: str):
        """Process and store research document"""
        response = requests.post(f"{self.base_url}/api/document/process", json={
            "file_path": file_path,
            "pipeline": "research",
            "options": {
                "extract_citations": True,
                "fact_checking": True,
                "entity_recognition": True
            },
            "store_in": ["cognee", "memos", "llamacloud"]
        })
        
        return response.json()

# Usage
assistant = ResearchAssistant()
results = assistant.research_topic("machine learning interpretability")
print(json.dumps(results, indent=2))
```

### Example 2: Code Documentation System

```javascript
class CodeDocumentationSystem {
    constructor() {
        this.baseUrl = 'http://localhost:8505';
    }
    
    async indexCodebase(projectPath) {
        const response = await fetch(`${this.baseUrl}/api/document/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: projectPath,
                pipeline: 'code',
                options: {
                    syntax_highlighting: true,
                    dependency_analysis: true,
                    generate_examples: true,
                    extract_apis: true
                },
                store_in: ['cognee', 'llamacloud']
            })
        });
        
        return await response.json();
    }
    
    async findCodeExamples(query) {
        const response = await fetch(`${this.baseUrl}/api/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: `code examples for ${query}`,
                mode: 'smart',
                options: {
                    filter_by_type: 'code',
                    include_syntax: true,
                    auto_optimize: true
                }
            })
        });
        
        return await response.json();
    }
}

// Usage
const docSystem = new CodeDocumentationSystem();
await docSystem.indexCodebase('/path/to/project');
const examples = await docSystem.findCodeExamples('authentication middleware');
console.log(examples);
```

### Example 3: Multi-Memory Chat Bot

```python
import asyncio
from typing import List, Dict

class MultiMemoryChatBot:
    def __init__(self):
        self.base_url = "http://localhost:8505"
        self.conversation_history = []
    
    async def chat(self, user_message: str) -> str:
        """Chat with context from multiple memory systems"""
        
        # Build query with conversation context
        context_query = self._build_context_query(user_message)
        
        # Query memory systems
        memory_response = await self._query_memories(context_query)
        
        # Generate response using retrieved context
        response = await self._generate_response(user_message, memory_response)
        
        # Store conversation in memory
        await self._store_conversation(user_message, response)
        
        return response
    
    def _build_context_query(self, message: str) -> str:
        """Build query incorporating conversation history"""
        recent_context = self.conversation_history[-5:]  # Last 5 exchanges
        context_str = " ".join([f"User: {h['user']} Bot: {h['bot']}" 
                               for h in recent_context])
        return f"Context: {context_str} Current question: {message}"
    
    async def _query_memories(self, query: str) -> Dict:
        """Query all memory systems for relevant information"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/query", json={
                "query": query,
                "mode": "sequential",
                "sources": ["cognee", "memento", "memos"],
                "options": {
                    "max_results": 10,
                    "context_building": True,
                    "include_metadata": True
                }
            }) as response:
                return await response.json()
    
    async def _generate_response(self, user_message: str, memory_context: Dict) -> str:
        """Generate response using memory context"""
        # Integrate with your LLM here
        # This is a simplified example
        relevant_info = memory_context.get('results', [])
        
        if relevant_info:
            context_summary = " ".join([r.get('content', '')[:200] 
                                      for r in relevant_info[:3]])
            response = f"Based on what I know: {context_summary}... "
        else:
            response = "I don't have specific information about that, but "
        
        return response + "let me help you with your question."
    
    async def _store_conversation(self, user_message: str, bot_response: str):
        """Store conversation in memory systems"""
        conversation_entry = {
            "user": user_message,
            "bot": bot_response,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Store in memory systems
        import aiohttp
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.base_url}/api/document/process", json={
                "content": json.dumps(conversation_entry),
                "pipeline": "conversation",
                "store_in": ["memento", "memos"]
            })

# Usage
bot = MultiMemoryChatBot()
response = await bot.chat("How do I implement OAuth2 authentication?")
print(response)
```

## 🎯 Use Cases

### 1. Knowledge Management System
- Unified search across all organizational knowledge
- Automatic document processing and indexing
- Context-aware query responses

### 2. Development Assistant
- Code example search across multiple repositories
- API documentation query and retrieval
- Best practices and pattern recommendations

### 3. Research Platform
- Academic paper analysis and synthesis
- Citation tracking and fact verification
- Cross-reference discovery

### 4. Customer Support System
- Multi-source knowledge base queries
- Conversation history integration
- Automated response suggestions

### 5. Content Management
- Multi-format document processing
- Semantic search and classification
- Version tracking and synchronization

## 🔧 Troubleshooting

### Common Issues

#### Memory System Connection Failures

```bash
# Check individual system health
curl http://localhost:8505/api/systems/health

# Verify network connectivity
docker-compose exec unified-query-service ping cognee
docker-compose exec unified-query-service ping memento-mcp

# Check configuration
docker-compose exec unified-query-service cat config/systems.yaml
```

#### Query Performance Issues

```bash
# Monitor query performance
curl http://localhost:8505/api/analytics/performance

# Check cache status
curl http://localhost:8505/api/cache/status

# Optimize query parameters
# Use more specific queries
# Limit result count
# Enable caching
```

#### Document Processing Failures

```bash
# Check LlamaParse API key
echo $LLAMA_INDEX_API_KEY

# Verify file permissions
ls -la /path/to/documents

# Check processing logs
make logs-unified-query-service | grep "document_processor"
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export UQS_DEBUG=true

# Restart service
make restart

# View debug logs
make logs-unified-query-service
```

### Performance Tuning

```yaml
# Optimize configuration for performance
performance:
  max_concurrent_queries: 100
  query_timeout: "60s"
  memory_limit: "4GB"
  cpu_limit: "4.0"
  
  caching:
    enabled: true
    aggressive_caching: true
    cache_warming: true
  
  connection_pooling:
    max_connections: 50
    connection_timeout: "10s"
```

The Unified Query Service is a powerful orchestration layer that brings together multiple memory systems into a cohesive, intelligent query interface. Its integration with document processing and workflow management makes it an essential component for building sophisticated AI-powered applications.