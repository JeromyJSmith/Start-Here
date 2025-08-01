# SuperClaude Framework - Python with uv
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

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv && \
    uv pip install -r pyproject.toml

# Copy source code
COPY . .

# Install the package in development mode
RUN uv pip install -e .

# Create cache directory
RUN mkdir -p /app/.uv-cache

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import SuperClaude; print('OK')" || exit 1

# Development command
CMD ["python", "-m", "SuperClaude"]