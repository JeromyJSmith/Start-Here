# CLI Tool - Node.js with pnpm
FROM node:18-alpine as base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@8.15.0 --activate

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy source code
COPY . .

# Create symlinks for bin commands
RUN pnpm link --global

# Expose port for analytics
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "console.log('OK')" || exit 1

# Development command
CMD ["pnpm", "run", "analytics:start"]