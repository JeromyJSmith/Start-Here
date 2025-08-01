# n8n Nodes Siteboon - TypeScript with pnpm
FROM node:18-alpine as base

# Install pnpm and system dependencies
RUN corepack enable  corepack prepare pnpm@latest --activate  \
    apk add --no-cache python3 make g++

# Set pnpm environment
ENV PNPM_HOME=/pnpm
ENV PATH=/pnpm:$PATH

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY pnpm-lock.yaml ./
COPY tsconfig.json* ./

# Install dependencies
RUN pnpm install --frozen-lockfile --prod

# Copy source code
COPY . .

# Build TypeScript
RUN if [ -f tsconfig.json ]; then pnpm run build || npm run build || echo "No build script found"; fi

# Install n8n globally for development
RUN pnpm add -g n8n

# Expose n8n port
EXPOSE 5678

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5678 || exit 1

# Development command
CMD ["pnpm", "run", "start"]
