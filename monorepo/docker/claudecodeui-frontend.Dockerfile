# ClaudeCodeUI Frontend - React/Vite with pnpm
FROM node:18-alpine as base

# Install pnpm
RUN corepack enable  corepack prepare pnpm@latest --activate

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

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5173 || exit 1

# Development command
CMD ["pnpm", "run", "dev"]
