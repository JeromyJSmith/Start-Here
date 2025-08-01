# Command Reference

Complete reference for all commands available in the Claude Code Monorepo system.

## 📋 Table of Contents

- [Makefile Commands](#makefile-commands) - Docker orchestration and development
- [Claude Code Commands](#claude-code-commands) - Core AI assistant commands
- [SuperClaude Commands](#superclaude-commands) - Enhanced framework commands
- [CLI Tool Commands](#cli-tool-commands) - Analytics and project setup
- [API Endpoints](#api-endpoints) - REST API reference
- [Docker Commands](#docker-commands) - Direct container management

## 🔧 Makefile Commands

The Makefile provides the primary interface for managing the entire monorepo.

### Setup & Environment

| Command | Description | Usage |
|---------|-------------|-------|
| `make help` | Show all available commands | `make help` |
| `make setup` | Initial setup - copy .env and create directories | `make setup` |
| `make clean` | Stop services and clean up containers/volumes | `make clean` |

### Development Workflow

| Command | Description | Usage |
|---------|-------------|-------|
| `make dev` | Start all services in development mode | `make dev` |
| `make dev-detached` | Start all services in background | `make dev-detached` |
| `make stop` | Stop all services | `make stop` |
| `make restart` | Restart all services | `make restart` |
| `make build` | Build all Docker images | `make build` |
| `make build-SERVICE` | Build specific service | `make build-frontend` |

### Dependency Management

| Command | Description | Usage |
|---------|-------------|-------|
| `make install-deps` | Install all dependencies | `make install-deps` |
| `make install-python` | Install Python dependencies with uv | `make install-python` |
| `make install-node` | Install Node.js dependencies with pnpm | `make install-node` |

### Testing & Quality

| Command | Description | Usage |
|---------|-------------|-------|
| `make test` | Run all tests | `make test` |
| `make test-python` | Run Python tests | `make test-python` |
| `make test-node` | Run Node.js tests | `make test-node` |
| `make test-integration` | Run integration tests | `make test-integration` |
| `make lint` | Run all linters | `make lint` |
| `make format` | Format all code | `make format` |

### Monitoring & Debugging

| Command | Description | Usage |
|---------|-------------|-------|
| `make health` | Check health of all services | `make health` |
| `make logs` | Show logs from all services | `make logs` |
| `make logs-SERVICE` | Show logs from specific service | `make logs-frontend` |

### Shell Access

| Command | Description | Usage |
|---------|-------------|-------|
| `make shell-superclaude` | Access SuperClaude Framework container | `make shell-superclaude` |
| `make shell-frontend` | Access Frontend container | `make shell-frontend` |
| `make shell-backend` | Access Backend container | `make shell-backend` |
| `make shell-cli` | Access CLI Tool container | `make shell-cli` |
| `make shell-postgres` | Access PostgreSQL CLI | `make shell-postgres` |
| `make shell-redis` | Access Redis CLI | `make shell-redis` |

### Database Operations

| Command | Description | Usage |
|---------|-------------|-------|
| `make db-migrate` | Run database migrations | `make db-migrate` |
| `make db-seed` | Seed database with sample data | `make db-seed` |
| `make db-reset` | Reset database | `make db-reset` |

### Production & Backup

| Command | Description | Usage |
|---------|-------------|-------|
| `make prod-build` | Build for production | `make prod-build` |
| `make prod-up` | Start production environment | `make prod-up` |
| `make backup` | Backup volumes and data | `make backup` |
| `make security-scan` | Run security scans | `make security-scan` |

### Quick Workflows

| Command | Description | Usage |
|---------|-------------|-------|
| `make quick-start` | Setup, install deps, start, check health | `make quick-start` |
| `make quick-test` | Quick test of core functionality | `make quick-test` |
| `make quick-clean` | Clean and restart everything | `make quick-clean` |

## 🤖 Claude Code Commands

Core Claude Code commands for AI-powered development.

### Basic Commands

```bash
# Start Claude Code in current directory
claude

# Get help
claude --help

# Check version
claude --version

# Run specific command
claude "implement user authentication"
```

### Advanced Usage

```bash
# Use with specific files
claude --files src/app.js,src/config.js "optimize performance"

# Generate commit messages
claude --git "review changes and generate commit message"

# Code review
claude --review "analyze this pull request"
```

## 🚀 SuperClaude Commands

Enhanced framework commands with specialized AI personas.

### Command Structure

All SuperClaude commands use the `/sc:` prefix:

```bash
/sc:command [arguments] [--flags]
```

### Development Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:implement` | Feature implementation with persona selection | `/sc:implement user-auth --type api` |
| `/sc:build` | Build and compilation tasks | `/sc:build --target production` |
| `/sc:design` | Design and architecture planning | `/sc:design --domain frontend` |

### Analysis Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:analyze` | Multi-dimensional analysis | `/sc:analyze --scope project --focus security` |
| `/sc:troubleshoot` | Problem investigation | `/sc:troubleshoot --symptoms "slow queries"` |
| `/sc:explain` | Educational explanations | `/sc:explain --topic "async programming"` |

### Quality Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:improve` | Evidence-based enhancement | `/sc:improve --target performance` |
| `/sc:test` | Testing workflows | `/sc:test --type integration` |
| `/sc:cleanup` | Technical debt reduction | `/sc:cleanup --scope codebase` |

### Utility Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:document` | Documentation generation | `/sc:document --type api-docs` |
| `/sc:git` | Git workflow assistance | `/sc:git --operation merge-conflicts` |
| `/sc:estimate` | Task estimation | `/sc:estimate --feature auth-system` |

### Meta Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/sc:task` | Long-term project management | `/sc:task --create "refactor auth"` |
| `/sc:index` | Command catalog browsing | `/sc:index --category analysis` |
| `/sc:load` | Project context loading | `/sc:load --path ./project` |
| `/sc:spawn` | Task orchestration | `/sc:spawn --mode parallel` |

### Common Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--plan` | Show execution plan | `/sc:implement feature --plan` |
| `--think` | Enable multi-file analysis | `/sc:analyze --think` |
| `--uc` | Ultra-compressed output | `/sc:improve --uc` |
| `--validate` | Pre-operation validation | `/sc:build --validate` |
| `--persona-X` | Force specific persona | `/sc:analyze --persona-security` |

### Persona Auto-Activation

SuperClaude automatically activates appropriate personas:

- **architect**: System design, scalability
- **frontend**: UI/UX, accessibility  
- **backend**: APIs, infrastructure
- **security**: Vulnerabilities, compliance
- **analyzer**: Root cause analysis
- **performance**: Optimization
- **qa**: Testing, quality assurance

## 🛠️ CLI Tool Commands

Analytics and project configuration commands.

### Interactive Usage

```bash
# Run interactive setup
npx claude-code-templates

# Quick analytics dashboard
npx claude-code-templates --analytics

# System health check
npx claude-code-templates --health-check
```

### Framework Setup

```bash
# React TypeScript project
npx claude-code-templates --language javascript-typescript --framework react --yes

# Python Django project  
npx claude-code-templates --language python --framework django --yes

# Show what would be installed
npx claude-code-templates --dry-run
```

### Analysis Tools

```bash
# Analyze existing commands
npx claude-code-templates --commands-stats

# Analyze automation hooks  
npx claude-code-templates --hooks-stats

# Analyze MCP configurations
npx claude-code-templates --mcps-stats
```

### Alternative Commands

All these work identically:
- `npx claude-code-templates`
- `npx cct` (super short)
- `npx claude-setup`
- `npx create-claude-config`

## 🌐 API Endpoints

REST API endpoints for programmatic access.

### Backend API (Port 3000)

#### Authentication
```bash
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/status
```

#### Projects
```bash
GET    /api/projects
POST   /api/projects
GET    /api/projects/:id
PUT    /api/projects/:id
DELETE /api/projects/:id
```

#### Git Operations
```bash
GET  /api/git/:project/status
POST /api/git/:project/commit
POST /api/git/:project/push
```

### Memory Service API (Port 8500)

#### Health Check
```bash
GET /health
```

#### Memory Operations
```bash
POST /api/memory/store
POST /api/memory/query
GET  /api/memory/status
```

### Unified Query Service API (Port 8505)

#### Query Operations
```bash
POST /api/query
{
  "query": "string",
  "mode": "unified|sequential|parallel|smart",
  "sources": ["cognee", "memento", "memos", "llamacloud"],
  "options": {
    "max_results": 10,
    "include_metadata": true
  }
}
```

#### Document Processing
```bash
POST /api/document/process
{
  "file_path": "string",
  "pipeline": "default|custom",
  "output_format": "markdown|json|structured"
}
```

#### Workflow Management
```bash
POST /api/workflow/deploy
GET  /api/workflow/status/:id
POST /api/workflow/trigger/:id
```

### Analytics API (Port 3001)

#### Real-time Data
```bash
GET /api/analytics/sessions
GET /api/analytics/conversations
GET /api/analytics/metrics
```

#### WebSocket Endpoints
```bash
ws://localhost:3001/ws/analytics
ws://localhost:3001/ws/notifications
```

## 🐳 Docker Commands

Direct Docker container management.

### Service Management

```bash
# Start specific services
docker-compose up claudecodeui-frontend
docker-compose up superclaude-framework

# Build and start
docker-compose up --build

# Scale services
docker-compose up --scale worker=3

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v
```

### Container Operations

```bash
# Execute commands in running containers
docker-compose exec frontend npm run build
docker-compose exec backend npm test

# Run one-off commands
docker-compose run --rm frontend npm install
docker-compose run --rm superclaude-framework python -c "import cognee"
```

### Logs and Debugging

```bash
# Follow logs
docker-compose logs -f
docker-compose logs -f frontend backend

# Container stats
docker stats

# Inspect containers
docker-compose ps
docker inspect monorepo_frontend_1
```

## 🎯 Usage Examples

### Complete Development Workflow

```bash
# 1. Setup new project
make setup
make install-deps

# 2. Start development
make dev-detached

# 3. Check everything is running
make health

# 4. Work with Claude Code
claude "create a new React component"

# 5. Use SuperClaude for complex tasks
claude "/sc:implement user-dashboard --persona-frontend"

# 6. Monitor with analytics
# Visit http://localhost:3001

# 7. Test your changes
make test

# 8. Format and lint
make format lint

# 9. Check logs if needed
make logs-frontend

# 10. Clean up when done
make stop
```

### Memory System Integration

```bash
# 1. Query unified memory system
curl -X POST http://localhost:8505/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "user authentication patterns",
    "mode": "unified",
    "sources": ["cognee", "memento", "memos"]
  }'

# 2. Process document
curl -X POST http://localhost:8505/api/document/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "pipeline": "default",
    "store_in": ["cognee", "memos"]
  }'
```

### Analytics Dashboard Usage

```bash
# 1. Start analytics dashboard
npx claude-code-templates --analytics

# 2. Monitor Claude Code sessions
# Visit http://localhost:3001

# 3. Export conversation data
# Use the web interface to export CSV/JSON

# 4. Health check the system
npx claude-code-templates --health-check
```

## 🔗 Command Chaining

Many commands can be chained for complex workflows:

```bash
# Complete setup and test
make setup && make install-deps && make dev-detached && make test

# Development cycle
make format && make lint && make test && make build

# Clean restart
make stop && make clean && make dev

# Production deployment
make prod-build && make prod-up && make health
```

## 🆘 Emergency Commands

When things go wrong:

```bash
# Nuclear option - reset everything
make clean && docker system prune -f && make setup && make dev

# Fix permissions
sudo chown -R $USER:$USER volumes/ && make restart

# Reset database
make db-reset && make restart

# Check what's consuming resources
docker stats
docker system df
```

This command reference covers all the ways you can interact with the Claude Code Monorepo system. For specific use cases and examples, check the [Examples section](../examples/README.md).