# Claude Code Monorepo

A comprehensive monorepo containing all Claude Code projects with Docker orchestration, automated workflows, and development tools.

## 🏗️ Architecture

This monorepo contains 7 integrated services:

### Python Services (uv package manager)
- **SuperClaude Framework** (`services/superclaude-framework`) - Core AI framework
- **Claude Code** (`services/claude-code`) - Main CLI application  
- **GenAI Stack** (`services/genai-stack`) - AI model stack with Ollama integration

### Node.js Services (pnpm workspace)
- **CLI Tool** (`services/cli-tool`) - Command-line interface with analytics
- **ClaudeCodeUI Frontend** (`services/claudecodeui-frontend`) - React/Vite web interface
- **ClaudeCodeUI Backend** (`services/claudecodeui-backend`) - Express.js API server
- **ClaudeCodeUI Plugin** (`services/claudecodeui-plugin`) - Plugin system
- **n8n Nodes Siteboon** (`services/n8n-nodes-siteboon`) - n8n automation nodes

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- pnpm 8+ (for Node.js packages)
- Python 3.11+ (for local development)

### 1. Clone and Setup
```bash
cd monorepo
make setup        # Copy .env and create directories
```

### 2. Start Development Environment
```bash
make dev          # Start all services with hot reload
# OR
make dev-detached # Start in background
```

### 3. Check Service Health
```bash
make health       # View service status and URLs
```

## 🔧 Development Workflow

### Service URLs (Development)
- **Frontend**: http://localhost:5173 (React/Vite with HMR)
- **Backend API**: http://localhost:3000 (Express.js)
- **SuperClaude**: http://localhost:8001 (Python framework)
- **GenAI Stack**: http://localhost:8003 (AI models)
- **CLI Analytics**: http://localhost:3001 (Node.js analytics)
- **n8n Interface**: http://localhost:5678 (Automation)
- **Ollama**: http://localhost:11434 (LLM server)

### Common Commands
```bash
# Development
make dev                    # Start all services
make logs                   # View all logs
make logs-frontend          # View specific service logs
make stop                   # Stop all services
make restart                # Restart all services

# Dependencies
make install-deps           # Install all dependencies
make install-python         # Install Python deps with uv
make install-node           # Install Node.js deps with pnpm

# Testing
make test                   # Run all tests
make test-python            # Python tests only
make test-node              # Node.js tests only

# Code Quality
make lint                   # Lint all code
make format                 # Format all code

# Database
make db-migrate             # Run migrations
make db-reset               # Reset database

# Shell Access
make shell-frontend         # Access frontend container
make shell-backend          # Access backend container
make shell-superclaude      # Access Python framework
```

## 📦 Package Management

### Node.js (pnpm workspace)
```bash
# Install for all workspaces
pnpm install

# Install for specific service
pnpm --filter claudecodeui-frontend add react-query

# Run scripts
pnpm --filter cli-tool run test
```

### Python (uv)
```bash
# In any Python service
uv add fastapi
uv sync
uv pip install -r requirements.txt
```

## 🔄 Hot Reload Configuration

All services are configured for hot reload in development:

- **React/Vite**: Instant HMR via Vite dev server
- **Express.js**: Auto-restart via nodemon
- **Python**: File watching with automatic container restart
- **TypeScript**: Incremental compilation

## 🐳 Docker Configuration

### Service Architecture
```
monorepo/
├── docker-compose.yml      # Main orchestration
├── docker-compose.dev.yml  # Development overrides  
├── docker/                 # Individual Dockerfiles
├── volumes/                # Persistent data
└── services/               # Service source code
```

### Volumes and Persistence
- **postgres_data**: PostgreSQL database
- **sqlite_data**: SQLite databases
- **redis_data**: Redis cache
- **shared_data**: Cross-service data
- **node_modules_cache**: Node.js dependencies
- **uv_cache**: Python package cache

## 🔧 Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database
POSTGRES_DB=claude_code
POSTGRES_USER=claude
POSTGRES_PASSWORD=development

# APIs
VITE_API_URL=http://localhost:3000
CLAUDE_API_URL=http://localhost:8001

# Security
JWT_SECRET=your-secret-key

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
```

## 🧪 Testing Strategy

### Test Types
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **End-to-End Tests**: Full workflow testing

### Test Commands
```bash
make test                   # All tests
make test-integration       # Integration tests
make quick-test            # Core functionality test
```

## 📊 Monitoring and Debugging

### Health Checks
```bash
make health                 # Service status
make logs                   # All logs
make logs-backend          # Specific service
```

### Database Access
```bash
make shell-postgres        # PostgreSQL CLI
make shell-redis          # Redis CLI
```

### Service Debugging
```bash
make shell-frontend        # Debug React app
make shell-backend         # Debug Express API
make shell-superclaude     # Debug Python framework
```

## 🔐 Security

### Development Security
- JWT authentication for API access
- Environment variable isolation
- Database user permissions
- Container network isolation

### Production Considerations
- Change default passwords
- Enable SSL/TLS
- Configure firewalls
- Regular security updates

## 📚 Service Documentation

Each service contains detailed documentation:

- [SuperClaude Framework](services/superclaude-framework/README.md)
- [CLI Tool](services/cli-tool/README.md)
- [ClaudeCodeUI Frontend](services/claudecodeui-frontend/README.md)
- [ClaudeCodeUI Backend](services/claudecodeui-backend/README.md)
- [GenAI Stack](services/genai-stack/README.md)

## 🚀 Production Deployment

### Build for Production
```bash
make prod-build            # Production builds
make prod-up               # Production deployment
```

### Backup and Restore
```bash
make backup                # Backup all data
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test: `make test`
4. Ensure code quality: `make lint format`
5. Submit pull request

## 📋 Troubleshooting

### Common Issues

**Services won't start:**
```bash
make clean                 # Clean containers and volumes
make setup                 # Recreate environment
make dev                   # Start fresh
```

**Port conflicts:**
- Check `.env` file for port configurations
- Ensure no other services are using the same ports

**Database issues:**
```bash
make db-reset              # Reset database
make db-migrate            # Run migrations
```

**Permission issues:**
```bash
sudo chown -R $USER:$USER volumes/
```

### Getting Help

- Check service logs: `make logs-[service-name]`
- Access service shell: `make shell-[service-name]`
- Review service health: `make health`
- Consult individual service documentation

## 📄 License

MIT License - see individual service licenses for details.