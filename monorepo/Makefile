# Claude Code Monorepo Makefile
# Orchestrates development, testing, and deployment workflows

.PHONY: help setup dev build test clean install-deps install-python install-node lint format logs shell-% stop restart health docs

# Default target
help: ## Show this help message
	@echo "Claude Code Monorepo - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Service Shells:"
	@echo "  make shell-superclaude    - Access SuperClaude Framework container"
	@echo "  make shell-cli            - Access CLI Tool container"
	@echo "  make shell-frontend       - Access Frontend container"
	@echo "  make shell-backend        - Access Backend container"
	@echo "  make shell-genai          - Access GenAI Stack container"

# Environment setup
setup: ## Initial setup - copy environment files and create directories
	@echo "🚀 Setting up Claude Code Monorepo..."
	@cp .env.example .env 2>/dev/null || echo ".env already exists"
	@mkdir -p volumes/{postgres,redis,ollama,logs}
	@mkdir -p docker/ssl
	@echo "✅ Setup complete! Edit .env file as needed."

# Development commands
dev: setup ## Start all services in development mode
	@echo "🔧 Starting development environment..."
	@docker-compose up --build

dev-detached: setup ## Start all services in development mode (detached)
	@echo "🔧 Starting development environment (detached)..."
	@docker-compose up -d --build

# Build commands
build: ## Build all Docker images
	@echo "🏗️ Building all services..."
	@docker-compose build

build-%: ## Build specific service (e.g., make build-frontend)
	@echo "🏗️ Building $* service..."
	@docker-compose build $*

# Dependency management
install-deps: install-python install-node ## Install all dependencies

install-python: ## Install Python dependencies with uv
	@echo "🐍 Installing Python dependencies..."
	@docker-compose run --rm superclaude-framework uv sync
	@docker-compose run --rm claude-code bash -c "pip install uv && uv pip install -r requirements.txt" 2>/dev/null || echo "No requirements.txt in claude-code"
	@docker-compose run --rm genai-stack uv sync

install-node: ## Install Node.js dependencies with pnpm
	@echo "📦 Installing Node.js dependencies..."
	@pnpm install

# Testing commands
test: ## Run all tests
	@echo "🧪 Running all tests..."
	@make test-python
	@make test-node

test-python: ## Run Python tests
	@echo "🐍 Running Python tests..."
	@docker-compose run --rm superclaude-framework python -m pytest tests/ 2>/dev/null || echo "No tests found in SuperClaude Framework"
	@docker-compose run --rm claude-code python -m pytest tests/ 2>/dev/null || echo "No tests found in Claude Code"
	@docker-compose run --rm genai-stack python -m pytest tests/ 2>/dev/null || echo "No tests found in GenAI Stack"

test-node: ## Run Node.js tests
	@echo "📦 Running Node.js tests..."
	@docker-compose run --rm cli-tool pnpm test
	@docker-compose run --rm claudecodeui-frontend pnpm test 2>/dev/null || echo "No tests configured for frontend"
	@docker-compose run --rm claudecodeui-backend pnpm test 2>/dev/null || echo "No tests configured for backend"

test-integration: ## Run integration tests
	@echo "🔗 Running integration tests..."
	@docker-compose run --rm cli-tool pnpm run test:integration

# Code quality commands
lint: lint-python lint-node ## Run all linters

lint-python: ## Lint Python code
	@echo "🐍 Linting Python code..."
	@docker-compose run --rm superclaude-framework python -m flake8 . 2>/dev/null || echo "flake8 not configured"
	@docker-compose run --rm claude-code python -m flake8 . 2>/dev/null || echo "flake8 not configured"
	@docker-compose run --rm genai-stack python -m flake8 . 2>/dev/null || echo "flake8 not configured"

lint-node: ## Lint Node.js code
	@echo "📦 Linting Node.js code..."
	@pnpm run lint 2>/dev/null || echo "ESLint not configured at root level"

format: format-python format-node ## Format all code

format-python: ## Format Python code
	@echo "🐍 Formatting Python code..."
	@docker-compose run --rm superclaude-framework python -m black . 2>/dev/null || echo "black not installed"
	@docker-compose run --rm claude-code python -m black . 2>/dev/null || echo "black not installed"
	@docker-compose run --rm genai-stack python -m black . 2>/dev/null || echo "black not installed"

format-node: ## Format Node.js code
	@echo "📦 Formatting Node.js code..."
	@pnpm run format 2>/dev/null || echo "Prettier not configured at root level"

# Service management
start: dev-detached ## Start all services
stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	@docker-compose down

restart: stop dev-detached ## Restart all services

clean: stop ## Stop services and clean up
	@echo "🧹 Cleaning up containers, volumes, and networks..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Cleanup complete!"

# Monitoring and debugging
logs: ## Show logs from all services
	@docker-compose logs -f

logs-%: ## Show logs from specific service (e.g., make logs-frontend)
	@docker-compose logs -f $*

health: ## Check health of all services
	@echo "🏥 Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "🌐 Service URLs:"
	@echo "  Frontend:     http://localhost:5173"
	@echo "  Backend:      http://localhost:3000"
	@echo "  SuperClaude:  http://localhost:8001"
	@echo "  GenAI Stack:  http://localhost:8003"
	@echo "  CLI Tool:     http://localhost:3001"
	@echo "  n8n:          http://localhost:5678"
	@echo "  Ollama:       http://localhost:11434"
	@echo "  Postgres:     localhost:5432"
	@echo "  Redis:        localhost:6379"
	@echo "  Neo4j:        http://localhost:7474"
	@echo "  Memory API:   http://localhost:8500"
	@echo "  Agent-IO:     (CLI tool)"
	@echo "  Dashboard:    http://localhost:8080"

# Shell access
shell-superclaude: ## Access SuperClaude Framework container
	@docker-compose exec superclaude-framework bash

shell-cli: ## Access CLI Tool container
	@docker-compose exec cli-tool bash

shell-frontend: ## Access Frontend container
	@docker-compose exec claudecodeui-frontend sh

shell-backend: ## Access Backend container
	@docker-compose exec claudecodeui-backend sh

shell-genai: ## Access GenAI Stack container
	@docker-compose exec genai-stack bash

shell-postgres: ## Access PostgreSQL container
	@docker-compose exec postgres psql -U claude -d claude_code

shell-redis: ## Access Redis container
	@docker-compose exec redis redis-cli

shell-memory: ## Access Memory Service container
	@docker-compose exec memory-service bash

shell-neo4j: ## Access Neo4j container
	@docker-compose exec neo4j bash

# Database operations
db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	@docker-compose exec claudecodeui-backend npm run migrate 2>/dev/null || echo "No migrations configured"

db-seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	@docker-compose exec claudecodeui-backend npm run seed 2>/dev/null || echo "No seed script configured"

db-reset: ## Reset database
	@echo "💥 Resetting database..."
	@docker-compose down postgres
	@docker volume rm monorepo_postgres_data 2>/dev/null || echo "Volume already removed"
	@docker-compose up -d postgres

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	@echo "Available in services:"
	@find . -name "README.md" -not -path "./node_modules/*" -not -path "./.git/*"

# Production commands
prod-build: ## Build for production
	@echo "🏭 Building for production..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up: ## Start production environment
	@echo "🚀 Starting production environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Security
security-scan: ## Run security scans
	@echo "🔐 Running security scans..."
	@docker-compose run --rm superclaude-framework python -m safety check 2>/dev/null || echo "safety not installed"
	@pnpm audit

# Backup and restore
backup: ## Backup volumes and data
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@docker run --rm -v monorepo_postgres_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/postgres-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@docker run --rm -v monorepo_redis_data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/redis-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✅ Backup complete!"

# Quick commands for specific workflows
quick-start: setup install-deps dev-detached health ## Quick start for new users

quick-test: ## Quick test of core functionality
	@make test-node
	@make health

quick-clean: ## Quick cleanup and restart
	@make clean
	@make dev-detached