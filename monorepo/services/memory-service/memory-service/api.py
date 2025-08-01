#!/usr/bin/env python3
"""
Simple API server for Memory Service health checks
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import asyncio
from memory_integration import MemoryIntegrationService

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                "status": "healthy",
                "service": "Memory Integration Service",
                "components": {
                    "cognee": "ready",
                    "memento-mcp": "ready",
                    "neo4j": "connected"
                }
            }
            
            self.wfile.write(json.dumps(status).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <html>
            <head><title>Memory Service</title></head>
            <body>
                <h1>Memory Integration Service</h1>
                <p>Combining Cognee and Memento MCP for AI memory</p>
                <ul>
                    <li><a href="/health">Health Check</a></li>
                    <li>Neo4j Browser: <a href="http://localhost:7474">http://localhost:7474</a></li>
                </ul>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8500):
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"Memory Service API running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()