#!/bin/bash
set -e

echo "Starting Memory Service (Simplified)..."

# Configure environment
export GRAPH_DATABASE_PROVIDER=neo4j
export GRAPH_DATABASE_URL=bolt://neo4j:7687
export GRAPH_DATABASE_USERNAME=neo4j
export GRAPH_DATABASE_PASSWORD=development
export VECTOR_ENGINE_PROVIDER=neo4j
export NEO4J_URI=bolt://neo4j:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=development
export NEO4J_DATABASE=neo4j
export MEMORY_STORAGE_TYPE=neo4j
export NEO4J_VECTOR_INDEX=entity_embeddings
export NEO4J_VECTOR_DIMENSIONS=1536
export NEO4J_SIMILARITY_FUNCTION=cosine

# Configure OpenAI for embeddings (if available)
if [ ! -z "$OPENAI_API_KEY" ]; then
    export LLM_API_KEY=$OPENAI_API_KEY
fi

echo "Memory Service is ready. Environment configured for Cognee and Memento MCP."
echo "Neo4j connection: bolt://neo4j:7687"
echo ""
echo "To use the memory service:"
echo "1. Cognee is available at /app/cognee"
echo "2. Memento MCP is available at /app/memento-mcp"
echo ""

# Keep container running
tail -f /dev/null