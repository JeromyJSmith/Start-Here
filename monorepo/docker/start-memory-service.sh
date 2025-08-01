#!/bin/bash
set -e

echo "Starting Memory Service with Cognee and Memento MCP..."

# No need to activate virtual environment - using system Python
cd /app/cognee

# Configure Cognee to use Neo4j
export GRAPH_DATABASE_PROVIDER=neo4j
export GRAPH_DATABASE_URL=bolt://neo4j:7687
export GRAPH_DATABASE_USERNAME=neo4j
export GRAPH_DATABASE_PASSWORD=development

# Configure vector storage
export VECTOR_ENGINE_PROVIDER=neo4j
export NEO4J_URI=bolt://neo4j:7687
export NEO4J_USERNAME=neo4j
export NEO4J_PASSWORD=development

# Configure OpenAI for embeddings (if available)
if [ ! -z "$OPENAI_API_KEY" ]; then
    export LLM_API_KEY=$OPENAI_API_KEY
fi

# Initialize Cognee
echo "Initializing Cognee..."
python -c "
import cognee
import asyncio

async def init():
    await cognee.prune.prune_system()
    await cognee.prune.prune_data() 
    print('Cognee initialized successfully')

asyncio.run(init())
"

# Start Memento MCP server in background
echo "Starting Memento MCP server..."
cd /app/memento-mcp
export MEMORY_STORAGE_TYPE=neo4j
export NEO4J_DATABASE=neo4j
export NEO4J_VECTOR_INDEX=entity_embeddings
export NEO4J_VECTOR_DIMENSIONS=1536
export NEO4J_SIMILARITY_FUNCTION=cosine
export DEBUG=true

# Run Memento MCP server
if [ -f dist/index.js ]; then
    node dist/index.js &
else
    echo "Memento MCP build not found, skipping..."
fi
MEMENTO_PID=$!

# Start Memory Service API server for health checks
echo "Starting Memory Service API..."
cd /app
python memory-service/api.py &
API_PID=$!

# Keep the container running and handle signals
trap "kill $MEMENTO_PID $API_PID" EXIT
wait