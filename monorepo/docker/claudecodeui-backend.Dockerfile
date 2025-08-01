# ClaudeCodeUI Backend - Express.js with pnpm
FROM node:18-alpine as base

# Install pnpm and system dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate && \
    apk add --no-cache python3 py3-setuptools make g++ && \
    ln -sf python3 /usr/bin/python

# Set pnpm environment
ENV PNPM_HOME=/pnpm
ENV PATH=/pnpm:$PATH

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile --prod

# Copy source code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Development command
CMD ["pnpm", "run", "dev"]