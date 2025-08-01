# ClaudeCodeUI Plugin - Node.js with pnpm
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

# Install dependencies if package.json exists
RUN if [ -f package.json ]; then pnpm install --frozen-lockfile --prod; fi

# Copy source code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "console.log('OK')" || exit 1

# Development command
CMD ["pnpm", "run", "dev"]
