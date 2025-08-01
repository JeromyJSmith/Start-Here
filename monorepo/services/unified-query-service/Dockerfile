# Unified Query Service
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python package managers
RUN pip install --upgrade pip uv

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY ./services/unified-query-service/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy llama_deploy for workflow deployment
COPY ./services/llama_deploy ./llama_deploy
RUN cd /app/llama_deploy && uv pip install --system -e .

# Copy service code
COPY ./services/unified-query-service ./unified-query-service

# Copy startup script
COPY ./docker/start-unified-query-service.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-unified-query-service.sh

# Expose ports
EXPOSE 8505 8000-8010

# Environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8505/health || exit 1

# Start the service
CMD ["/usr/local/bin/start-unified-query-service.sh"]