#!/bin/bash
set -e

echo "Starting LlamaCloud Service..."

# Configure environment
export LLAMA_CLOUD_API_KEY=${LLAMA_CLOUD_API_KEY}
export LLAMA_INDEX_API_KEY=${LLAMA_INDEX_API_KEY}
export NEO4J_URI=${NEO4J_URI:-bolt://neo4j:7687}
export NEO4J_USERNAME=${NEO4J_USERNAME:-neo4j}
export NEO4J_PASSWORD=${NEO4J_PASSWORD:-development}

echo "LlamaCloud Service Configuration:"
echo "- API Key: ${LLAMA_CLOUD_API_KEY:0:10}..."
echo "- Neo4j URI: $NEO4J_URI"
echo ""

# Create a simple health check endpoint
cat > /app/health_check.py << 'EOF'
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                "status": "healthy",
                "service": "LlamaCloud Integration Service",
                "components": {
                    "llamacloud-mcp": "ready",
                    "api_key": "configured" if os.getenv("LLAMA_CLOUD_API_KEY") else "missing"
                }
            }
            
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    import os
    server = HTTPServer(('', 8504), HealthHandler)
    print("Health check server running on port 8504")
    server.serve_forever()
EOF

# Start health check server in background
python /app/health_check.py &
HEALTH_PID=$!

echo "LlamaCloud Service is ready."
echo ""
echo "To use the service:"
echo "1. Configure Claude Code with the llamacloud MCP server"
echo "2. Create indexes in LlamaCloud dashboard"
echo "3. Use query_<index_name> and extract_<agent_name> tools"
echo ""

# Keep container running and handle signals
trap "kill $HEALTH_PID" EXIT
wait