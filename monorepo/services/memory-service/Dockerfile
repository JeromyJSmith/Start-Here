# Memory Service - Python with uv
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy Cognee
COPY ./services/cognee ./cognee

# Copy Memento MCP
COPY ./services/memento-mcp ./memento-mcp

# Copy integration scripts
COPY ./services/memory-service/memory-service ./memory-service

# Install Cognee dependencies globally
RUN cd /app/cognee && \
    uv pip install --system -e . && \
    uv pip install --system python-dotenv neo4j

# Install Memento MCP dependencies
RUN cd /app/memento-mcp && npm install

# Build Memento MCP
RUN cd /app/memento-mcp && npm run build

# Create startup script
COPY ./docker/start-memory-service-simple.sh /usr/local/bin/start-memory-service.sh
RUN chmod +x /usr/local/bin/start-memory-service.sh

# Expose ports
EXPOSE 8500 8501

# Environment variables
ENV PYTHONPATH="/app/cognee:$PYTHONPATH"
ENV PATH="/app/cognee/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8500/health || exit 1

# Start the memory service
CMD ["/usr/local/bin/start-memory-service.sh"]