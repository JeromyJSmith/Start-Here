#!/bin/bash
set -e

echo "Starting Unified Query Service..."

# Wait for dependencies
echo "Waiting for dependencies to be ready..."

# Wait for Redis
until nc -z redis 6379; do
  echo "Waiting for Redis..."
  sleep 2
done

# Wait for Neo4j
until nc -z neo4j 7687; do
  echo "Waiting for Neo4j..."
  sleep 2
done

# Wait for memory services
echo "Checking memory services..."
services=("memory-service:8500" "llamacloud-service:8504")

for service in "${services[@]}"; do
  host=$(echo $service | cut -d: -f1)
  port=$(echo $service | cut -d: -f2)
  
  until nc -z $host $port 2>/dev/null; do
    echo "Waiting for $host:$port..."
    sleep 2
  done
done

echo "All dependencies are ready!"

# Export environment variables
export PYTHONPATH="/app:$PYTHONPATH"
export SERVICE_NAME="unified-query-service"
export SERVICE_PORT=8505

# Log configuration
echo ""
echo "Unified Query Service Configuration:"
echo "- Service Port: $SERVICE_PORT"
echo "- Redis: $REDIS_URL"
echo "- Neo4j: $NEO4J_URI"
echo "- Memory Systems: Cognee, Memento, MemOS, LlamaCloud"
echo "- Workflows: Memory Sync, Document Ingestion, Query Enhancement, Maintenance"
echo ""

# Start the service
cd /app/unified-query-service
exec uvicorn src.main:app \
  --host 0.0.0.0 \
  --port $SERVICE_PORT \
  --workers 1 \
  --log-level info