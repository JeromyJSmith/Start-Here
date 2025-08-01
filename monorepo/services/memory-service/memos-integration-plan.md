# MemOS Integration Plan

## Overview
This document outlines the plan to integrate MemOS alongside the existing Cognee and Memento MCP memory systems.

## Benefits of Adding MemOS

1. **Enhanced Memory Types**: 
   - Activation Memory (KV cache) for faster context reuse
   - Parametric Memory for model adaptations
   - Advanced textual memory with proven performance improvements

2. **Superior Performance**:
   - 159% improvement in temporal reasoning
   - 67% improvement in open domain queries
   - Built-in benchmarking and metrics

3. **Better Architecture**:
   - Modular MemCube design for easy extension
   - Native MCP support with FastMCP
   - Multi-user support with access control

4. **Compatibility**:
   - Uses same Neo4j instance
   - MCP protocol compatible
   - Can coexist with current setup

## Integration Strategy

### Phase 1: Add MemOS Service (Week 1)
1. Create `services/memos-service/` directory
2. Add MemOS to docker-compose.yml
3. Configure to use existing Neo4j instance
4. Set up FastMCP server endpoint

### Phase 2: Configure MCP Integration (Week 1)
1. Add MemOS MCP to Claude Code settings
2. Create routing logic for memory operations
3. Test basic memory operations

### Phase 3: Migration Strategy (Week 2)
1. Keep Cognee for semantic graph operations
2. Use MemOS for:
   - User-specific memories
   - Conversation context (activation memory)
   - Model adaptations (parametric memory)
3. Create unified API layer

### Phase 4: Performance Testing (Week 2)
1. Benchmark memory operations
2. Compare with current setup
3. Optimize based on results

## Docker Service Configuration

```yaml
memos-service:
  build:
    context: .
    dockerfile: ./services/memos-service/Dockerfile
  container_name: memos-service
  ports:
    - "8502:8000"  # MemOS API
    - "8503:8501"  # MemOS MCP server
  environment:
    - NEO4J_URI=bolt://neo4j:7687
    - NEO4J_USER=neo4j
    - NEO4J_PASSWORD=development
    - OPENAI_API_KEY=${OPENAI_API_KEY}
    - MOS_TEXT_MEM_TYPE=tree_text  # Advanced memory type
  depends_on:
    - neo4j
  volumes:
    - ./services/memos:/app/src/memos
    - memos-data:/app/data
```

## MCP Configuration

```json
{
  "memos": {
    "type": "stdio",
    "command": "python",
    "args": ["-m", "memos.api.mcp_serve"],
    "env": {
      "NEO4J_URI": "bolt://neo4j:7687",
      "NEO4J_USER": "neo4j",
      "NEO4J_PASSWORD": "development",
      "PYTHONPATH": "/app/src"
    }
  }
}
```

## Usage Examples

### Basic Memory Operations
```python
# Create user
await mcp.call_tool("memos", "create_user", {
  "user_id": "user123",
  "role": "USER"
})

# Add memory
await mcp.call_tool("memos", "add", {
  "messages": [
    {"role": "user", "content": "I prefer Python for backend development"},
    {"role": "assistant", "content": "Noted! I'll keep that in mind for future suggestions."}
  ],
  "user_id": "user123"
})

# Search memory
results = await mcp.call_tool("memos", "search", {
  "query": "What programming languages does the user prefer?",
  "user_id": "user123"
})
```

### Advanced Features
```python
# Chat with memory context
response = await mcp.call_tool("memos", "chat", {
  "query": "Can you help me set up a new backend service?",
  "user_id": "user123"
})
# Response will include context about Python preference

# Create memory cube
await mcp.call_tool("memos", "create_cube", {
  "cube_name": "project_context",
  "owner_id": "user123"
})
```

## Migration Path

1. **Coexistence Phase** (Current Plan):
   - Run all three systems in parallel
   - Route different memory types to appropriate systems
   - Monitor performance and usage

2. **Optimization Phase** (Future):
   - Based on performance metrics, optimize routing
   - Potentially migrate some Cognee operations to MemOS
   - Keep Memento for simple key-value operations

3. **Consolidation Phase** (Optional):
   - If MemOS proves superior, gradually migrate all operations
   - Maintain backward compatibility through API layer

## Risk Mitigation

1. **Data Consistency**: All systems use same Neo4j instance
2. **Rollback Plan**: Services are independent, can disable any
3. **Performance**: Start with limited operations, scale based on metrics
4. **Compatibility**: MCP protocol ensures consistent interface

## Success Metrics

- Response time improvement >20%
- Memory retrieval accuracy >90%
- Successful multi-user support
- Activation memory hit rate >70%

## Next Steps

1. Create memos-service directory structure
2. Write Dockerfile for MemOS service
3. Update docker-compose.yml
4. Configure Claude Code MCP settings
5. Implement basic test cases