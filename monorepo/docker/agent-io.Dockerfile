# Agent-IO - Node.js with pnpm
FROM node:18-alpine as base

# Install pnpm and system dependencies
RUN corepack enable && corepack prepare pnpm@8.15.0 --activate && \
    apk add --no-cache python3 make g++

# Set working directory
WORKDIR /app

# Copy package files first
COPY package.json pnpm-workspace.yaml ./
COPY packages/core/package.json ./packages/core/
COPY packages/jsonl/package.json ./packages/jsonl/
COPY packages/stream/package.json ./packages/stream/
COPY packages/invoke/package.json ./packages/invoke/

# Install all dependencies
RUN pnpm install

# Copy source code
COPY . .

# Build the packages
RUN pnpm run build

# Create a startup script
RUN echo '#!/bin/sh\ncd /app\necho "Agent-IO is ready!"\necho "Available commands:"\necho "  node packages/stream/dist/cli.cjs - Run agent-io CLI"\necho "  pnpm run build - Rebuild packages"\necho ""\necho "Testing CLI:"\nnode packages/stream/dist/cli.cjs --help || echo "CLI not ready yet"\ntail -f /dev/null' > /usr/local/bin/start-agent-io.sh && \
    chmod +x /usr/local/bin/start-agent-io.sh

# Expose port for web service (if needed)
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD echo "Agent-IO container is running" || exit 1

# Default command - just keep container running
CMD ["tail", "-f", "/dev/null"]