# Claude Code - Python with uv
FROM python:3.11-slim as base

# Install system dependencies including Node.js for MCP servers
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy startup script
COPY ./docker/start-claude-code.sh /usr/local/bin/start-claude-code.sh
RUN chmod +x /usr/local/bin/start-claude-code.sh

# Copy Claude Code files
COPY ./services/claude-code ./claude-code/

# Copy SuperClaude Framework
COPY ./services/superclaude-framework ./superclaude-framework/

# Create directories for cache, MCP servers, examples, and logs
RUN mkdir -p /app/.uv-cache /app/mcp-servers /app/examples /app/logs

# Copy Claude Code enhancements
COPY ./services/claude-code/.claude /app/.claude
COPY ./services/claude-code/mcp-servers /app/mcp-servers
COPY ./services/claude-code/examples /app/examples
COPY ./services/claude-code/ENHANCEMENTS.md /app/

# Copy Memento MCP server for memory integration
COPY ./services/memento-mcp /app/mcp-servers/memento-mcp

# Build Memento MCP
RUN cd /app/mcp-servers/memento-mcp && \
    npm install && \
    npm run build

# Make hook scripts executable
RUN chmod +x /app/.claude/hooks/*.py

# Expose port
EXPOSE 8002

# Set up environment for SuperClaude
ENV PATH="/app/superclaude-framework/.venv/bin:$PATH"
ENV PYTHONPATH="/app/superclaude-framework:/app/claude-code:$PYTHONPATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import SuperClaude; print('SuperClaude OK')" || exit 1

# Development command - run startup script
CMD ["/usr/local/bin/start-claude-code.sh"]