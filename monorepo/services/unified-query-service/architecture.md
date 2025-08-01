# Unified Query Service Architecture

## Overview
A comprehensive query orchestration layer that unifies multiple memory systems (Cognee, Memento MCP, MemOS, LlamaCloud) with advanced document processing and workflow deployment.

## Architecture Diagram

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

## Core Components

### 1. Query Orchestrator
- **Unified API**: Single endpoint for all query types
- **Query Router**: Intelligently routes queries to appropriate systems
- **Result Aggregator**: Combines results from multiple sources
- **Ranking Engine**: Scores and ranks results by relevance

### 2. Document Processor
- **LlamaParse Integration**: Advanced document parsing
- **Pipeline Manager**: Configurable processing pipelines
- **Format Converter**: Handles multiple document formats
- **Metadata Extractor**: Enriches documents with metadata

### 3. Workflow Engine
- **LlamaDeploy Integration**: Production-ready workflows
- **Event-Driven Architecture**: Async workflow execution
- **State Management**: Tracks workflow progress
- **Error Recovery**: Automatic retry and fallback

## API Design

### Query Endpoints

```yaml
POST /api/query
{
  "query": "string",
  "mode": "unified|sequential|parallel|smart",
  "sources": ["cognee", "memento", "memos", "llamacloud"],
  "options": {
    "max_results": 10,
    "include_metadata": true,
    "ranking_strategy": "relevance|recency|hybrid"
  }
}

POST /api/document/process
{
  "file_path": "string",
  "pipeline": "default|custom",
  "output_format": "markdown|json|structured",
  "store_in": ["cognee", "memos", "llamacloud"]
}

POST /api/workflow/deploy
{
  "workflow_id": "string",
  "config": {},
  "triggers": ["event", "schedule", "manual"]
}
```

## Query Modes

### 1. Unified Mode
- Queries all systems in parallel
- Merges and deduplicates results
- Returns single ranked list

### 2. Sequential Mode
- Queries systems in order
- Uses previous results to refine next query
- Builds context progressively

### 3. Parallel Mode
- Queries all systems simultaneously
- Returns results grouped by source
- No deduplication or ranking

### 4. Smart Mode
- Analyzes query intent
- Selects optimal systems
- Applies appropriate strategy

## Document Processing Pipelines

### Default Pipeline
1. **Parse**: LlamaParse extracts content
2. **Chunk**: Intelligent text segmentation
3. **Embed**: Generate embeddings
4. **Enrich**: Add metadata and context
5. **Store**: Distribute to memory systems

### Custom Pipelines
- **Research Pipeline**: Citation extraction, fact checking
- **Code Pipeline**: Syntax highlighting, dependency analysis
- **Legal Pipeline**: Clause extraction, compliance checking
- **Medical Pipeline**: Entity recognition, terminology mapping

## Workflow Deployment

### Pre-built Workflows

1. **Memory Sync Workflow**
   - Synchronizes data across all memory systems
   - Handles conflicts and updates
   - Maintains consistency

2. **Document Ingestion Workflow**
   - Monitors document folders
   - Processes new documents automatically
   - Updates all relevant indexes

3. **Query Enhancement Workflow**
   - Analyzes query patterns
   - Suggests query improvements
   - Learns from user feedback

4. **Maintenance Workflow**
   - Cleans up old data
   - Optimizes indexes
   - Generates performance reports

## Implementation Stack

### Technology Choices
- **Framework**: FastAPI (Python)
- **Async Runtime**: asyncio with aiocache
- **Message Queue**: Redis Streams
- **Workflow Engine**: llama_deploy
- **Document Parser**: LlamaParse
- **Monitoring**: Prometheus + Grafana

### Memory System Integration
```python
class MemorySystemAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, options: dict) -> List[Result]:
        pass
    
    @abstractmethod
    async def store(self, content: str, metadata: dict) -> str:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass

class CogneeAdapter(MemorySystemAdapter):
    # Semantic graph queries
    
class MementoAdapter(MemorySystemAdapter):
    # Key-value memory access
    
class MemOSAdapter(MemorySystemAdapter):
    # Multi-type memory operations
    
class LlamaCloudAdapter(MemorySystemAdapter):
    # Document index queries
```

## Configuration

### Service Configuration
```yaml
unified_query_service:
  port: 8505
  
  memory_systems:
    cognee:
      enabled: true
      weight: 0.3
      timeout: 5s
    memento:
      enabled: true
      weight: 0.2
      timeout: 3s
    memos:
      enabled: true
      weight: 0.3
      timeout: 5s
    llamacloud:
      enabled: true
      weight: 0.2
      timeout: 10s
  
  document_processing:
    llamaparse:
      api_key: ${LLAMA_INDEX_API_KEY}
      parsing_instruction: "Extract all information"
    pipelines:
      - name: default
        steps: [parse, chunk, embed, enrich, store]
    storage:
      batch_size: 100
      parallel_workers: 4
  
  workflows:
    llama_deploy:
      control_plane_port: 8000
      service_port_range: [8001, 8010]
    enabled_workflows:
      - memory_sync
      - document_ingestion
      - query_enhancement
```

## Performance Optimizations

### Caching Strategy
- **Query Cache**: LRU cache for frequent queries
- **Result Cache**: TTL-based result caching
- **Embedding Cache**: Reuse computed embeddings
- **Document Cache**: Parsed document cache

### Parallel Processing
- **Async I/O**: All operations are async
- **Connection Pooling**: Reuse database connections
- **Batch Operations**: Group similar operations
- **Load Balancing**: Distribute load across systems

## Monitoring & Observability

### Metrics
- Query latency by system
- Cache hit rates
- Document processing throughput
- Workflow execution times
- Error rates and types

### Logging
- Structured logging with correlation IDs
- Query audit trail
- Performance profiling
- Error tracking with context

### Health Checks
- Individual system health
- End-to-end query testing
- Resource utilization
- Queue depths

## Security Considerations

### Authentication & Authorization
- API key authentication
- JWT for user sessions
- Role-based access control
- Query result filtering

### Data Protection
- Encryption in transit (TLS)
- Encryption at rest (database)
- PII detection and masking
- Audit logging

## Deployment Strategy

### Docker Compose Integration
```yaml
unified-query-service:
  build:
    context: .
    dockerfile: ./services/unified-query-service/Dockerfile
  ports:
    - "8505:8505"
  environment:
    - REDIS_URL=redis://redis:6379
    - NEO4J_URI=bolt://neo4j:7687
    - LLAMA_INDEX_API_KEY=${LLAMA_INDEX_API_KEY}
  depends_on:
    - redis
    - neo4j
    - cognee
    - memory-service
    - llamacloud-service
```

### Scaling Considerations
- Horizontal scaling with load balancer
- Read replicas for heavy query loads
- Queue-based workflow distribution
- Auto-scaling based on metrics