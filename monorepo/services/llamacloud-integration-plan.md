# LlamaCloud Integration Plan

## Overview
This document outlines the integration of LlamaIndex Cloud services into the monorepo.

## API Key
```bash
LLAMA_INDEX_API_KEY=llx-UXiBARTYyHk8go89qXy0vK75iDeuZKFnNqZjscoziXz5gn4Y
```

## Phase 1: LlamaCloud MCP Integration

### 1. Clone llamacloud-mcp
```bash
cd services/
git clone https://github.com/run-llama/llamacloud-mcp.git
```

### 2. Create Docker Service
```yaml
# docker-compose.yml addition
llamacloud-service:
  build:
    context: .
    dockerfile: ./services/llamacloud-service/Dockerfile
  container_name: llamacloud-service
  ports:
    - "8504:8000"  # LlamaCloud API
  environment:
    - LLAMA_INDEX_API_KEY=${LLAMA_INDEX_API_KEY}
    - NEO4J_URI=bolt://neo4j:7687
    - NEO4J_USERNAME=neo4j
    - NEO4J_PASSWORD=development
  depends_on:
    - neo4j
```

### 3. Configure Claude Code MCP
```json
{
  "llamacloud": {
    "command": "uvx",
    "args": [
      "llamacloud-mcp@latest",
      "--api-key-env", "LLAMA_INDEX_API_KEY",
      "--index", "main-index:Main document index for the monorepo"
    ]
  }
}
```

## Phase 2: Workflow Deployment with llama_deploy

### 1. Clone llama_deploy
```bash
cd services/
git clone https://github.com/run-llama/llama_deploy.git
```

### 2. Create Workflow Service
```python
# services/workflows/memory_workflow.py
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI

class MemoryEnhancedWorkflow(Workflow):
    @step
    async def query_memory(self, ev: StartEvent) -> StopEvent:
        query = ev.query
        
        # Query multiple memory systems
        cognee_results = await self.cognee.search(query)
        memos_results = await self.memos.search(query)
        llamacloud_results = await self.llamacloud.search(query)
        
        # Combine and rank results
        combined = self.merge_results(
            cognee_results, 
            memos_results, 
            llamacloud_results
        )
        
        return StopEvent(result=combined)
```

### 3. Deploy Configuration
```yaml
# llama_deploy.yml
name: memory-enhanced-system

control-plane:
  port: 8000

services:
  memory-workflow:
    name: memory-workflow
    path: ./services/workflows/memory_workflow.py
    port: 8001
```

## Phase 3: Document Processing Pipeline

### 1. LlamaParse Integration
```python
# services/document-processor/parser.py
from llama_parse import LlamaParse

parser = LlamaParse(
    api_key=os.getenv("LLAMA_INDEX_API_KEY"),
    result_type="markdown",
    parsing_instruction="Extract key information and maintain structure"
)

async def process_document(file_path):
    # Parse document
    documents = await parser.aload_data(file_path)
    
    # Store in multiple systems
    for doc in documents:
        # Store in Cognee for semantic analysis
        await cognee.add(doc.text, metadata=doc.metadata)
        
        # Store in MemOS for fast retrieval
        await memos.add({
            "messages": [{"role": "system", "content": doc.text}],
            "metadata": doc.metadata
        })
        
        # Index in LlamaCloud
        await llamacloud.index(doc)
```

## Phase 4: Unified Query Interface

### 1. Create Query Router
```python
# services/query-router/router.py
class UnifiedQueryRouter:
    def __init__(self):
        self.cognee = CogneeClient()
        self.memos = MemOSClient()
        self.llamacloud = LlamaCloudClient()
    
    async def query(self, query: str, context: dict):
        # Route based on query type
        if self._is_semantic_query(query):
            return await self.cognee.search(query)
        elif self._is_user_memory(query, context):
            return await self.memos.search(query, user_id=context['user_id'])
        elif self._is_document_query(query):
            return await self.llamacloud.search(query)
        else:
            # Query all systems and merge
            results = await asyncio.gather(
                self.cognee.search(query),
                self.memos.search(query),
                self.llamacloud.search(query)
            )
            return self._merge_results(results)
```

## Benefits of Integration

1. **Document Processing**: LlamaParse for complex document parsing
2. **Scalable Deployment**: llama_deploy for production workflows
3. **MCP Integration**: Direct Claude integration via llamacloud-mcp
4. **Unified Memory**: Combine Cognee, MemOS, and LlamaCloud

## Environment Variables

```bash
# .env additions
LLAMA_INDEX_API_KEY=llx-UXiBARTYyHk8go89qXy0vK75iDeuZKFnNqZjscoziXz5gn4Y
LLAMACLOUD_BASE_URL=https://api.llamaindex.ai
```

## Testing Strategy

1. **Unit Tests**: Test each service independently
2. **Integration Tests**: Test cross-service communication
3. **E2E Tests**: Test complete workflows
4. **Performance Tests**: Benchmark query speeds

## Monitoring

1. **Service Health**: Monitor each service endpoint
2. **Query Performance**: Track response times
3. **Memory Usage**: Monitor resource consumption
4. **Error Rates**: Track and alert on failures

## Next Steps

1. Clone llamacloud-mcp repository
2. Create Dockerfile for LlamaCloud service
3. Update docker-compose.yml
4. Configure MCP in Claude Code
5. Test basic LlamaCloud queries
6. Implement workflow deployment
7. Create unified query interface