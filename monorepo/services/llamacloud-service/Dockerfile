# LlamaCloud Service
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy llamacloud-mcp
COPY ./services/llamacloud-mcp ./llamacloud-mcp

# Install llamacloud-mcp and dependencies
RUN cd /app/llamacloud-mcp && \
    uv pip install --system -e .

# Create startup script
COPY ./docker/start-llamacloud-service.sh /usr/local/bin/start-llamacloud-service.sh
RUN chmod +x /usr/local/bin/start-llamacloud-service.sh

# Expose ports
EXPOSE 8504

# Environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8504/health || exit 1

# Start the service
CMD ["/usr/local/bin/start-llamacloud-service.sh"]