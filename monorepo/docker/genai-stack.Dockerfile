# GenAI Stack - Python with uv
FROM python:3.11-slim as base

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

# Copy requirements
COPY requirements.txt ./

# Create virtual environment and install dependencies
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

# Copy source code
COPY . .

# Create cache directory
RUN mkdir -p /app/.uv-cache

# Expose ports
EXPOSE 8003 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Activate venv in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Development command
CMD ["/app/.venv/bin/python", "api.py"]